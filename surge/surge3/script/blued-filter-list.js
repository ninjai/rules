const keyword = $persistentStore.read('filterBlued') !== null ? $persistentStore.read('filterBlued') : ''

function filterList(data) {
  switch (keyword) {
    case 'normal': {
      return data.filter(item => item.note === '' && item.is_invisible_half === 0)
    }
    case 'general': {
      return data.filter(item => item.note !== '拒-丑' && item.is_invisible_half === 0)
    }
    default: {
      return data.filter(item => item.note === keyword && item.is_invisible_half === 0)
    }
  }
}

if (typeof $response != 'undefined') {
  let obj = JSON.parse($response.body)
  if (obj.data) {
    obj.data = filterList(obj.data)
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