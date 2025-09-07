self.addEventListener('install', event => {
  console.log('Service Worker: Installed');
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  console.log('Service Worker: Activated');
});

self.addEventListener('fetch', event => {
  // For now, let all requests pass through
});
