const headers = $request.headers

$persistentStore.write(JSON.stringify(headers), 'headersBlued')

$done({})