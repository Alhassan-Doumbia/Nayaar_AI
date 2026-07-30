// Manifest PWA de Nayaar — fichier spécial Next.js (App Router), généré et
// lié automatiquement dans le <head> (pas besoin d'un <link rel="manifest"> manuel).
// Icônes : monogramme "N" doré sur fond noir Nayaar, voir frontend/public/icon-*.png.
export default function manifest() {
  return {
    name: "Nayaar — Conseiller Olfactif",
    short_name: "Nayaar",
    description: "L'assistant olfactif intelligent de Maison Nayaar.",
    start_url: "/",
    display: "standalone",
    orientation: "portrait",
    background_color: "#faf7f2", // --nayaar-cream, couleur de l'écran de démarrage
    theme_color: "#faf7f2", // --nayaar-cream, couleur de la barre système (cohérente avec le Header)
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icon-512-maskable.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
