const url = $request.url

const id = url.match(/[0-9]{4,}/)[0]

if ($persistentStore.read('IdBlued') === null) {
  $persistentStore.write(id, 'IdBlued')
}

$done({})