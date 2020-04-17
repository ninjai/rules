if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    obj.data = obj.data.filter(item => item.note === '')
  }
  $done({ body: JSON.stringify(obj) })
}
else {
  $done({})
}