if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    obj.data = obj.data.filter(item => item.note === '')
  }
  if (obj.extra) {
    if (obj.extra.adms) {
      if (obj.extra.adms.data) {
        obj.extra.adms.data.length = 0
      }
    }
  }
  $done({ body: JSON.stringify(obj) })
}
else {
  $done({})
}