function filterList(data) {
  return data.filter(item => item.note === '' && item.is_invisible_half === 0)
}

function listGetMore(start) {
  let data = []
  let url = $request.url.match(/(^.*)start\=(\d+)(.*$)/)
  start = start + Number.parseInt(url[2], 10)
  url = `${url[1]}start=${start}${url[3]}`
  $httpClient.get({ url }, (error, response, data) => {
    if (error) {
      $notification.post('获取更多失败', '', error)
      console.log(url)
      return []
    } else {
      let obj = JSON.parse(data)
      if (obj.data) {
        $notification.post('获取更多成功', '', '')
        return filterList(data)
      }
      else {
        return []
      }
    }
  })
}

if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    obj.data = filterList(obj.data)
    let n = 1
    while (obj.data.length < 10) {
      obj.data = [...obj.data, ...listGetMore(60 * n)]
      n++
    }
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