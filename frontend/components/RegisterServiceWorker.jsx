"use client";

import { useEffect } from "react";

/**
 * Enregistre le service worker (public/sw.js) au chargement de l'app —
 * condition nécessaire (avec le manifest, voir app/manifest.js) pour que
 * le navigateur propose l'installation en PWA sur mobile. Ne rend rien à
 * l'écran, échoue silencieusement si l'API est indisponible (ex. navigateur
 * trop ancien) plutôt que de casser le reste de l'application.
 */
export function RegisterServiceWorker() {
  useEffect(() => {
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js").catch(() => {
      // installation PWA non critique : l'app reste utilisable sans service worker
    });
  }, []);

  return null;
}
