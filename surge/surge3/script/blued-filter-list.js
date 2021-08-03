const keyword = $persistentStore.read('filterBlued') !== null ? $persistentStore.read('filterBlued') : ''

function filterList(data) {
  switch (keyword) {
    case 'normal':
      {
        return data.filter(item => item.note === '')
      }
    case 'general':
      {
        return data.filter(item => item.note !== '拒-丑')
      }
    default:
      {
        return data.filter(item => item.note === keyword)
      }
  }
}

if (typeof $response !== 'undefined') {
  let original = JSON.parse($response.body)
  let modified = JSON.parse(JSON.stringify(original))

  if (modified.data) {
    modified.data = filterList(modified.data)

    if (!modified.data.length) {
      modified.data = original.data.splice(-1)
    }
  }

  $done({ body: JSON.stringify(modified) })
} else {
  $done({})
}