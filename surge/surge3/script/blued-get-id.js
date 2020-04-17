const url = $request.url

const id = url.match(/[0-9]{4,}/)[0]

console.log(id)

if ($persistentStore.read('IdBlued') === null) {
  $persistentStore.write(id, 'IdBlued')
  $notification.post('获取ID成功', '', id)
}
else if ($persistentStore.read('IdBlued') != id) {
  $persistentStore.write(id, 'IdBlued')
  $notification.post('更新ID成功', '', id)
}
else {
  $notification.post('欢迎回来', '', id)
}

$done({})