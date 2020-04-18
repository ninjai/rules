if (typeof $response != 'undefined') {
  const obj = JSON.parse($response.body)

  if (obj.data[0].note === '') {
    if ($persistentStore.read('IdBlued')) {
      const id = obj.data[0].uid
      const name = obj.data[0].name
      const headers = JSON.parse($persistentStore.read('headersBlued'))

      const options = {
        'url': `https://argo.blued.cn/users/${$persistentStore.read('IdBlued')}/notes`,
        'headers': headers,
        'body': {
          'uid': id,
          'note': '拒-丑'
        }
      }

      $httpClient.post(options, function(error, response, data) {
        if (error) {
          $notification.post('备注失败', name, error)
        } else {
          $notification.post('备注成功', '', name)
        }
      })
    }
    else {
      $notification.post('请先获取ID', '', '')
    }
  }
}


$done({})  