if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    if ($request.url.includes('splash')) {
      obj.data = []
    }
    else if ($request.url.includes('users')) {
      obj.data = obj.data.filter(item => item.name != '')
    }
  }
  $done({ body: JSON.stringify(obj) })
}
else {
  $done({})
}