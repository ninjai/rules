const headers = $request.headers

delete headers['Content-Lengt']

delete headers['If-None-Match']

$persistentStore.write(JSON.stringify(headers), 'headersBlued')

$done({})