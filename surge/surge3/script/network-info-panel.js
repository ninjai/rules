let ssid = $network.wifi.ssid
let radio = $network["cellular-data"].radio
let v4 = $network.v4.primaryAddress
let routerv4 = $network.v4.primaryRouter
let v6 = $network.v6.primaryAddress
let routerv6 = $network.v6.primaryRouter

$done({
    "title": "IP Information",
    "content": "无线网络: ${ssid}\nIPv4: ${IPv4}\nIPv6: ${IPv6}\nIPv4网关: ${routerv4}\nIPv6网关: ${routerv6}",
    "icon": "wifi",
    "icon-color": "#0EEA3B",
 })