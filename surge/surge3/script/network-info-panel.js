let bssid = $network.wifi.bssid
let ssid = $network.wifi.ssid
let carrier = $network["cellular-data"].carrier
let radio = $network["cellular-data"].radio
let v4 = $network.v4.primaryAddress
let routerv4 = $network.v4.primaryRouter
let v6 = $network.v6.primaryAddress

if(ssid!=='undefined'){
    $done({
        "title": "网络信息",
        "content": `无线网络: ${ssid}\nIPv4: ${v4}\nIPv6: ${v6}\nIPv4网关: ${routerv4}`,
        "icon": "wifi",
        "icon-color": "#0EEA3B",
    })
}
else{
    $done({
        "title": "网络信息",
        "content": `移动网络: ${carrier},${radio}\nIPv4: ${v4}\nIPv6: ${v6}\nIPv4网关: ${routerv4}`,
        "icon": "simcard.fill",
        "icon-color": "#EA0300",
    })
}
