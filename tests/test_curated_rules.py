"""规则整理回归：覆盖范围、参数保留、原始快照和生成物一致性。"""

import importlib.util
import ipaddress
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT / 'scripts/build-curated-rules.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def domain_match(records, host):
    return any((f[0] == 'DOMAIN' and host == f[1]) or
               (f[0] == 'DOMAIN-SUFFIX' and (host == f[1] or host.endswith('.' + f[1]))) or
               (f[0] == 'DOMAIN-KEYWORD' and f[1] in host) for f, _ in records)


def ip_match(records, ip):
    address = ipaddress.ip_address(ip)
    return any(address in ipaddress.ip_network(f[1]) for f, _ in records
               if f[0] in {'IP-CIDR', 'IP-CIDR6'})


class NormalizeTests(unittest.TestCase):
    def test_review_date_is_per_list(self):
        outputs, _ = builder.build()
        media = outputs[builder.PROVIDER / 'curated/media/netflix.list'].decode()
        other = outputs[builder.PROVIDER / 'curated/media/apple-news.list'].decode()
        self.assertIn('# 审阅日期: 2026-10-06', media)
        self.assertIn('# 审阅日期: 2026-09-29', other)

    def test_duplicates_keep_flags(self):
        rows = builder.parse('DOMAIN,a.example\nDOMAIN,a.example // 重复\nDOMAIN,a.example,extended-matching')
        clean, _ = builder.clean(rows, {})
        self.assertEqual(len(clean), 2)

    def test_suffix_coverage_preserves_boundaries_and_flags(self):
        rows = builder.parse('DOMAIN,a.example.com\nDOMAIN-SUFFIX,example.com\n'
                             'DOMAIN,notexample.com\nDOMAIN,a.example.com,extended-matching')
        clean, _ = builder.clean(rows, {})
        self.assertEqual(len(clean), 3)
        self.assertTrue(domain_match(clean, 'a.example.com'))
        self.assertTrue(domain_match(clean, 'notexample.com'))
        self.assertFalse(domain_match(clean, 'example.com.invalid'))

    def test_cidr_canonicalization(self):
        clean, _ = builder.clean(builder.parse('IP-CIDR,223.119.62.225/28,no-resolve'), {})
        self.assertEqual(clean[0][0], ('IP-CIDR', '223.119.62.224/28', 'no-resolve'))
        self.assertTrue(ip_match(clean, '223.119.62.225'))
        self.assertFalse(ip_match(clean, '223.119.62.240'))

    def test_ipv4_prefix_is_not_a_domain_keyword(self):
        clean, _ = builder.clean(builder.parse('DOMAIN-KEYWORD,101.226.129.'), {'convert_ipv4_keywords': True})
        self.assertTrue(ip_match(clean, '101.226.129.1'))
        self.assertFalse(ip_match(clean, '101.226.130.1'))
        self.assertFalse(domain_match(clean, 'x101.226.129.example.com'))
        self.assertIn('no-resolve', clean[0][0])

    def test_unknown_rules_and_stale_removals_fail(self):
        for text in ('BOGUS,example.com', 'DOMAIN,example.com,Proxy', 'DOMAIN,'):
            with self.assertRaises(ValueError):
                builder.parse(text)
        with self.assertRaises(ValueError):
            builder.clean([], {'remove': {'DOMAIN,missing.example': 'old decision'}})

    def test_ip_partition_is_stable(self):
        clean, _ = builder.clean(builder.parse('IP-CIDR,1.2.3.0/24,no-resolve\nDOMAIN,a.example\n'
                                               'USER-AGENT,Example*\nIP-ASN,123,no-resolve'), {})
        self.assertEqual([f[0] for f, _ in clean], ['DOMAIN', 'USER-AGENT', 'IP-CIDR', 'IP-ASN'])


class PublishedRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs, cls.report = builder.build()

    def rules(self, name):
        return builder.parse(self.outputs[builder.PROVIDER / 'curated' / name].decode())

    def test_build_reproducible(self):
        second, _ = builder.build()
        self.assertEqual(self.outputs, second)
        for path, data in self.outputs.items():
            self.assertEqual(path.read_bytes(), data, str(path))

    def test_telegram_official_ranges(self):
        rows = self.rules('apps/telegram.list')
        self.assertTrue(domain_match(rows, 'api.telegram.org'))
        self.assertTrue(ip_match(rows, '149.154.160.1'))
        self.assertTrue(ip_match(rows, '2001:b28:f23d::1'))
        self.assertFalse(ip_match(rows, '5.28.200.1'))
        self.assertFalse(any(f[0] == 'IP-ASN' for f, _ in rows))

    def test_shared_cdn_and_private_ip(self):
        self.assertFalse(domain_match(self.rules('media/youtube.list'), 'edgedl.me.gvt1.com'))
        self.assertTrue(domain_match(self.rules('apps/google-search.list'), 'edgedl.me.gvt1.com'))
        self.assertTrue(domain_match(self.rules('media/youtube.list'), 'rr1.googlevideo.com'))
        self.assertFalse(ip_match(self.rules('apps/teamviewer.list'), '172.16.102.56'))

    def test_news_merged_without_losing_audio(self):
        rows = self.rules('media/apple-news.list')
        self.assertTrue(domain_match(rows, 'news-edge.apple.com'))
        self.assertTrue(any('podcast' in f[1] for f, _ in rows if f[0] == 'URL-REGEX'))
        self.assertEqual(sum(r['output'] == 'media/apple-news.list' for r in self.report['lists']), 1)

    def test_all_wechat_prefixes(self):
        source = builder.parse((builder.PROVIDER / 'vendor/blackmatrix7/wechat.list').read_text())
        rows = self.rules('apps/wechat.list')
        prefixes = [f[1] for f, _ in source if f[0] == 'DOMAIN-KEYWORD']
        self.assertEqual(len(prefixes), 233)
        for prefix in prefixes:
            self.assertTrue(ip_match(rows, prefix + '1'), prefix)
            self.assertFalse(domain_match(rows, 'x' + prefix + 'example.invalid'), prefix)


if __name__ == '__main__':
    unittest.main()
