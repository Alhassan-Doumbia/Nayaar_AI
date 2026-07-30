// Service worker minimal de Nayaar.
//
// Ne met RIEN en cache volontairement : les réponses du chat et les
// recommandations viennent d'un appel API en direct (backend/app/main.py)
// et ne doivent jamais être servies périmées depuis un cache. Sa seule
// présence, avec un écouteur "fetch", suffit aux critères d'installabilité
// PWA de Chrome/Android (icône + manifest + service worker enregistré).
self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (evenement) => {
  evenement.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (evenement) => {
  const requete = evenement.request;
  const memeOrigine = new URL(requete.url).origin === self.location.origin;

  // On n'intercepte QUE les requêtes de navigation same-origin en GET (le
  // strict nécessaire pour l'installabilité). Toute autre requête — en
  // particulier les appels POST vers l'API (autre origine : port 8000,
  // potentiellement une IP réseau différente sur mobile) — n'est PAS prise
  // en charge ici : on ne rappelle pas respondWith(), donc le navigateur la
  // traite nativement, sans repasser par le service worker.
  //
  // C'était la cause du bug "impossible d'envoyer un prompt" sur mobile :
  // rejouer une requête POST cross-origin via fetch(event.request) dans le
  // contexte d'un service worker peut échouer (corps de requête mal
  // repropagé) — d'où le "TypeError: Failed to fetch" observé dans sw.js,
  // qui empêchait purement et simplement l'appel à /api/chat d'aboutir.
  if (requete.method !== "GET" || !memeOrigine) {
    return;
  }

  evenement.respondWith(fetch(requete));
});
