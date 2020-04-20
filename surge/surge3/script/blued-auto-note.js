if (typeof $response != 'undefined') {
  const obj = JSON.parse($response.body)


  if (obj.data[0].note === '') {
    if ($persistentStore.read('IdBlued')) {

      const id = obj.data[0].uid
      const name = obj.data[0].name
      const headers = JSON.parse($persistentStore.read('headersBlued'))

      const options = {
        'url': `https://argo.blued.cn/users/${$persistentStore.read('IdBlued')}/notes`,
        headers,
        'body': {
          'uid': id,
          'note': '拒-丑'
        }
      }

      $httpClient.post(options, function(error, response, data) {
        if (error) {
          $notification.post('备注失败', name, error)
        } else {
          $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('备注成功', '', name)
        }
      })
    }
    else {
      $notification.post('请先获取ID', '', '')
    }
  }

  if ($persistentStore.read('ViewCountBlued') === null) {
    let obj = {
      'count': 1,
      'startTime': new Date()
    }
    $persistentStore.write(JSON.stringify(obj), 'ViewCountBlued')
  } else {
    let obj = JSON.parse($persistentStore.read('ViewCountBlued'))
    obj = { ...obj, ...{ 'count': ++obj.count } }
    $persistentStore.write(JSON.stringify(obj), 'ViewCountBlued')
    if (obj.count % 100 === 0) {
      let startTime = new Date(obj.startTime)
      $notification.post('累计浏览人数', '', `自${startTime.toLocaleString('zh-CN')}以来共浏览了${obj.count}人`)
    }
  }
}

$done({})