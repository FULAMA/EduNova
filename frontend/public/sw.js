const CACHE_NAME = 'edunova-static-v2'
const CACHE_PREFIX = 'edunova-static-'
const APP_SHELL = '/index.html'
const STATIC_ASSETS = [
  '/',
  APP_SHELL,
  '/manifest.webmanifest',
  '/favicon.svg',
  '/icons/edunova-192.svg',
  '/icons/edunova-512.svg',
]

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME)
    const shellResponse = await fetch(APP_SHELL)
    if (shellResponse.ok) {
      const html = await shellResponse.clone().text()
      await cache.put(APP_SHELL, shellResponse)
      const assets = [...html.matchAll(/(?:src|href)="(\/assets\/[^\"]+)"/g)]
        .map((match) => match[1])
      await cache.addAll([...STATIC_ASSETS.filter((path) => path !== APP_SHELL), ...assets])
    } else {
      await cache.addAll(STATIC_ASSETS)
    }
    await self.skipWaiting()
  })())
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
        .map((key) => caches.delete(key)),
    )),
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const request = event.request
  const url = new URL(request.url)

  // Protected data and API traffic are network-only. Only same-origin app files enter the cache.
  if (request.method !== 'GET' || url.origin !== self.location.origin) return

  if (request.mode === 'navigate') {
    event.respondWith(fetch(request).catch(async () => {
      const shell = await caches.match(APP_SHELL)
      return shell || Response.error()
    }))
    return
  }

  if (!url.pathname.startsWith('/assets/')) return

  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cached = await cache.match(request)
      if (cached) return cached
      const response = await fetch(request)
      if (response.ok) await cache.put(request, response.clone())
      return response
    }),
  )
})
