const CACHE_NAME = 'minha-carteira-v2';
const STATIC_CACHE = [
  '/static/css/custom.css',
  '/static/css/dark-mode.css',
  '/static/css/fab.css',
  '/static/vendor/bootstrap/css/bootstrap.min.css',
  '/static/vendor/bootstrap/js/bootstrap.bundle.min.js',
  '/static/vendor/bootstrap-icons/font/bootstrap-icons.min.css',
  '/static/vendor/chartjs/chart.umd.min.js',
  '/static/img/logo.png',
  '/static/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_CACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);

  // Nunca intercepte POST/PUT/DELETE: formulários e ações AJAX devem ir à rede.
  if (request.method !== 'GET') return;

  // Não armazene respostas privadas, login, logout ou API no cache do dispositivo.
  if (
    url.origin !== self.location.origin ||
    url.pathname.startsWith('/accounts/') ||
    url.pathname.startsWith('/api/') ||
    url.pathname.startsWith('/admin/')
  ) {
    return;
  }

  const isStatic = url.pathname.startsWith('/static/');

  if (isStatic) {
    event.respondWith(
      caches.match(request).then(cached => {
        const network = fetch(request).then(response => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
          }
          return response;
        });
        return cached || network;
      })
    );
    return;
  }

  // Não armazene páginas HTML: elas podem conter dados financeiros privados.
  // Se estiver offline, o navegador exibirá a própria tela de indisponibilidade.
  event.respondWith(fetch(request));
});
