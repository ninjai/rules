if ($persistentStore.read('NotificaitonBlued') === 'open') {
  $persistentStore.write('close', 'NotificaitonBlued')
  $notification.post('通知关闭', '', '')
}
else {
  $persistentStore.write('open', 'NotificaitonBlued')
  $notification.post('通知开启', '', '')
}

if (typeof $request != 'undefined') {
  const url = $request.url
  const id = url.match(/[0-9]{4,}/)[0]

  if ($persistentStore.read('IdBlued') === null) {
    $persistentStore.write(id, 'IdBlued')
    $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('获取ID成功', '', id)
  }
  else if ($persistentStore.read('IdBlued') != id) {
    $persistentStore.write(id, 'IdBlued')
    $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('更新ID成功', '', id)
  }
  else {
    $persistentStore.read('NotificaitonBlued') === 'open' && $notification.post('欢迎回来', '', id)
  }
}

$done({})