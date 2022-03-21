if (typeof $response != 'undefined') {
  const obj = JSON.parse($response.body)

  obj.data[0].relationship = 0
  obj.data[0].privacy_photos_has_locked = 0

  $done({ body: JSON.stringify(obj) })
}
else {
  $done({})
}

