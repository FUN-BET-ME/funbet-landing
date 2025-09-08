// ✅ Required for OneSignal push
importScripts("https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.sw.js");

// ✅ Your own caching logic
const CACHE = 'funbet-pwa-v1';
const OFFLINE_URLS = ['/', '/logo.png', '/icons/site.webmanifest'];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await cache.addAll(OFFLINE_URLS);
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map(k => k !== CACHE && caches.delete(k)));
    self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;

  e.respondWith((async () => {
    try {
      const net = await fetch(e.request);
      const cache = await caches.open(CACHE);
      cache.put(e.request, net.clone());
      return net;
    } catch {
      const cached = await caches.match(e.request);
      return cached || caches.match('/');
    }
  })());
});
