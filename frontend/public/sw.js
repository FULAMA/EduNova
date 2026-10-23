const CACHE_NAME = 'edunova-static-v1'
const STATIC_ASSETS = ['/','/index.html','/manifest.webmanifest','/favicon.svg']

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS)))
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)),
    )),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  const url = new URL(request.url)

  // Never cache API responses or non-GET requests containing private data.
  const isStaticAsset = STATIC_ASSETS.includes(url.pathname)
    || /\.(?:css|js|svg|woff2?)$/i.test(url.pathname)
  if (request.method !== 'GET' || request.mode === 'navigate' || !isStaticAsset) return

  event.respondWith(
    caches.match(request).then((cached) => cached || fetch(request).then((response) => {
      if (url.origin === self.location.origin && response.ok) {
        const copy = response.clone()
        void caches.open(CACHE_NAME).then((cache) => cache.put(request, copy))
      }
      return response
    })),
  )
})
