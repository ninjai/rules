const headers = $request.headers
const obj = $response.body
const id = obj.data.uid
const name = obj.data.name

const options = {
  'url': 'https://argo.blued.cn/users/21253364/notes'
  'headers': headers,
  'body': {
    "uid": id,
    "note": "拒-丑"
  }
}

$httpClient.post(options, function(error, response, data) {
  if (error) {
    $notification.post("备注失败", name, error);
  }
  else 「
  $notification.post("备注成功", name, data);
})

$done({})