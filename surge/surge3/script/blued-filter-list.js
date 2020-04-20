if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    obj.data = obj.data.filter(item => item.note === '')
  }
  if (obj.extra) {
    if (obj.extra.adms) {
      obj.extra.adms.length = 0
    }
    if (obj.extra.adms_user) {
      obj.extra.adms_user.length = 0
    }
  }
  $done({ body: JSON.stringify(obj) })
}
else {
  $done({})
}