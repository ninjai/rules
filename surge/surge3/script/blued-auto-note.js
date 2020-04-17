const headers = JSON.parse($persistentStore.read('headersBlued'))

console.log(headers)

const obj = JSON.parse($response.body)

console.log(obj.data)

const id = obj.data.uid
const name = obj.data.name

const options = {
  'url': 'https://argo.blued.cn/users/21253364/notes',
  'headers': headers,
  'body': {
    'uid': id,
    'note': '拒-丑'
  }
}

console.log(options)

if (obj.data.note === '') {
  $httpClient.post(options, function(error, response, data) {
    if (error) {
      $notification.post('备注失败', name, error)
    } else {
      $notification.post('备注成功', name, data)
    }
  })
}

$done({})