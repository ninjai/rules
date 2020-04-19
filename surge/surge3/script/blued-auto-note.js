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
          $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('备注失败', name, error)
        } else {
          $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('备注成功', '', name)
        }
      })
    }
    else {
      $notification.post('请先获取ID', '', '')
    }

    if ($persistentStore.read('ViewCountBlued') === null) {
      let count = 1
      $persistentStore.write(count.toString(), 'ViewCountBlued')
      console.log('unchanged')
    } else {
      let count = Number.parseInt($persistentStore.read('ViewCountBlued'), 10)
      $persistentStore.write((count++).toString(), 'ViewCountBlued')
      console.log(count)
      if (count % 100 === 0) {
        $notification.post('累计浏览人数', '', count.toString())
      }
    }
  }
}

$done({})