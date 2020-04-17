$notification.post('获取头文件', '', '')

const headers = $request.headers

$persistentStore.write(JSON.stringify(headers), 'headersBlued')

$done({})