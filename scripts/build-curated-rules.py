#!/usr/bin/env python3
"""整理 Surge 发布规则；输入 curated-plan.json 和来源文件，输出 curated/ 与审计记录。
用法：python3 scripts/build-curated-rules.py [--check]；全程离线，不下载、不推送。
"""

import argparse
import hashlib
import ipaddress
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROVIDER = ROOT / 'surge/surge3/provider'
IP_TYPES = {'IP-CIDR', 'IP-CIDR6', 'IP-ASN'}
TYPES = IP_TYPES | {'DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD', 'USER-AGENT',
                    'PROCESS-NAME', 'URL-REGEX'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def parse(text):
    """仅解析当前来源所用语法；未知类型/额外字段直接报错，不静默丢弃。"""
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        parts = re.split(r'\s+//', line, maxsplit=1)
        rule = parts[0].strip()
        fields = tuple(v.strip() for v in rule.split(','))
        if len(fields) < 2 or fields[0] not in TYPES or not fields[1]:
            raise ValueError(f'不支持的规则，第 {number} 行：{rule}')
        if any(v not in {'no-resolve', 'extended-matching'} for v in fields[2:]):
            raise ValueError(f'不支持的参数，第 {number} 行：{rule}')
        result.append((fields, parts[1].strip() if len(parts) > 1 else ''))
    return result


def clean(records, entry):
    """去重只在同一策略集内执行，flags 不同的规则不合并。"""
    result, changes, removed = [], [], set()
    for fields, comment in records:
        original = ','.join(fields)
        if original in entry.get('remove', {}):
            changes.append({'action': 'remove', 'before': original,
                            'reason': entry['remove'][original]})
            removed.add(original)
            continue
        if entry.get('replace_ip_with') and fields[0] in IP_TYPES:
            changes.append({'action': 'remove', 'before': original,
                            'reason': '以 Telegram 官方精确 CIDR 清单替代历史 IP/ASN 范围'})
            continue
        if entry.get('convert_ipv4_keywords') and fields[0] == 'DOMAIN-KEYWORD':
            if not re.fullmatch(r'(?:\d{1,3}\.){3}', fields[1]):
                raise ValueError(f'不能安全转换的 IPv4 前缀：{original}')
            network = ipaddress.IPv4Network(fields[1] + '0/24')
            fields = ('IP-CIDR', str(network), 'no-resolve')
            changes.append({'action': 'convert', 'before': original,
                            'after': ','.join(fields),
                            'reason': '将来源中的 IPv4 三段前缀明确为 /24，避免匹配含数字的无关域名'})
        if fields[0] in {'IP-CIDR', 'IP-CIDR6'}:
            network = ipaddress.ip_network(fields[1], strict=False)
            if network.version != (4 if fields[0] == 'IP-CIDR' else 6):
                raise ValueError(f'IP 版本不匹配：{original}')
            canonical = (fields[0], str(network), *fields[2:])
            if canonical != fields:
                changes.append({'action': 'canonicalize', 'before': ','.join(fields),
                                'after': ','.join(canonical),
                                'reason': '规范网络地址写法，保留原前缀长度和网络范围'})
            fields = canonical
        result.append((fields, comment))
    if removed != set(entry.get('remove', {})):
        raise ValueError('待移除规则已变化，必须重新审核：' + str(set(entry['remove']) - removed))
    for addition in entry.get('add', []):
        result.extend(parse(addition['rule']))
        changes.append({'action': 'add', 'after': addition['rule'], 'reason': addition['reason']})
    if entry.get('replace_ip_with'):
        for value in (ROOT / entry['replace_ip_with']).read_text().splitlines():
            if not value.strip():
                continue
            network = ipaddress.ip_network(value.strip(), strict=True)
            fields = ('IP-CIDR' if network.version == 4 else 'IP-CIDR6', str(network), 'no-resolve')
            result.append((fields, 'Telegram 官方 CIDR'))
            changes.append({'action': 'add', 'after': ','.join(fields), 'reason': 'Telegram 官方 CIDR'})
    unique, seen = [], set()
    for fields, comment in result:
        if fields in seen:
            changes.append({'action': 'deduplicate', 'before': ','.join(fields)})
        else:
            seen.add(fields)
            unique.append((fields, comment))
    suffixes = {(fields[1], fields[2:]) for fields, _ in unique if fields[0] == 'DOMAIN-SUFFIX'}
    result = []
    for fields, comment in unique:
        if fields[0] in {'DOMAIN', 'DOMAIN-SUFFIX'}:
            labels = fields[1].split('.')
            start = 0 if fields[0] == 'DOMAIN' else 1
            covering = next(('.'.join(labels[i:]) for i in range(start, len(labels))
                             if ('.'.join(labels[i:]), fields[2:]) in suffixes), None)
            if covering:
                changes.append({'action': 'covered', 'before': ','.join(fields),
                                'by': 'DOMAIN-SUFFIX,' + covering})
                continue
        result.append((fields, comment))
    # 稳定分区：非 IP 规则在前，避免地址类规则提前触发 DNS；各区原有顺序不变。
    ordered = [r for r in result if r[0][0] not in IP_TYPES] + [r for r in result if r[0][0] in IP_TYPES]
    if ordered != result:
        changes.append({'action': 'order', 'reason': '域名/应用规则先于 IP/ASN，分区内保持原顺序'})
    return ordered, changes


def build():
    plan = json.loads((PROVIDER / 'curated-plan.json').read_text())
    vendor = json.loads((PROVIDER / 'vendor/manifest.json').read_text())
    for item in vendor['sources'] + vendor['licenses']:
        if digest((PROVIDER / 'vendor' / item['path']).read_bytes()) != item['sha256']:
            raise ValueError('原始快照被修改：' + item['path'])
    for source in plan['official_sources']:
        if 'file' in source and digest((ROOT / source['file']).read_bytes()) != source['sha256']:
            raise ValueError('官方快照被修改：' + source['file'])
    outputs, reports = {}, []
    for entry in plan['entries']:
        records, sources, attribution = [], [], []
        for source in entry['inputs']:
            data = (ROOT / source).read_bytes()
            text = data.decode('utf-8-sig')
            parsed = parse(text)
            records.extend(parsed)
            sources.append({'path': source, 'sha256': digest(data), 'rules': len(parsed)})
            # 上游元信息是历史快照信息；实际条数单独显示，保留作者及来源注释。
            header = []
            for line in text.splitlines():
                if line and not line.lstrip().startswith(('#', ';', '//')):
                    break
                if line.strip():
                    header.append('# 上游注释: ' + line.lstrip('#; /!'))
            attribution.extend(header)
        rules, changes = clean(records, entry)
        header = ['# 本仓库整理发布；请修改 curated-plan.json/来源并运行 scripts/build-curated-rules.py。',
                  '# 审阅日期: ' + entry.get('reviewed_on', plan['reviewed_on']), '# 有效规则数: ' + str(len(rules)),
                  '# 修改明细: surge/surge3/provider/curated/build-report.json',
                  '# 上游许可: surge/surge3/provider/vendor/licenses/']
        header += ['# 输入: ' + source for source in entry['inputs']]
        header += attribution
        body = ['# 非 IP 规则优先；IP/ASN 位于末尾，各类别内部保持来源顺序。']
        body += [','.join(fields) + (' // ' + comment if comment else '') for fields, comment in rules]
        data = ('\n'.join(header + [''] + body) + '\n').encode()
        output = PROVIDER / 'curated' / entry['output']
        if output in outputs:
            raise ValueError('重复输出路径：' + entry['output'])
        outputs[output] = data
        reports.append({'output': entry['output'], 'sources': sources, 'input_rules': len(records),
                        'output_rules': len(rules), 'sha256': digest(data), 'changes': changes})
    report = {'reviewed_on': plan['reviewed_on'], 'lists': reports,
              'total_input_rules': sum(r['input_rules'] for r in reports),
              'total_output_rules': sum(r['output_rules'] for r in reports)}
    outputs[PROVIDER / 'curated/build-report.json'] = (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode()
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只检查生成物是否最新，不写文件')
    args = parser.parse_args()
    outputs, report = build()
    # 遗留生成物也要报告，避免从计划删除后仍被设备引用。
    extra = set((PROVIDER / 'curated').rglob('*.list')) - set(outputs)
    if extra:
        raise ValueError('需人工处理的遗留文件：' + ', '.join(str(p) for p in extra))
    changed = []
    for path, data in outputs.items():
        if not path.exists() or path.read_bytes() != data:
            changed.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
    print(f"{len(report['lists'])} 个发布列表：{report['total_input_rules']} -> {report['total_output_rules']} 条规则")
    if args.check and changed:
        raise SystemExit('生成物需要更新：\n' + '\n'.join(changed))
    print('检查通过' if args.check else f'写入 {len(changed)} 个文件')


if __name__ == '__main__':
    main()
