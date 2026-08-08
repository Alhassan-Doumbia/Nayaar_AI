import { Lustria, Mulish } from "next/font/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import { RegisterServiceWorker } from "@/components/RegisterServiceWorker";
import "./globals.css";

// Serif éditoriale pour le logo « Nayaar », les titres et les noms de
// parfums — voir Docs/NAYAAR_DESIGN_DIRECTION.md, section 3.
const lustria = Lustria({
  variable: "--font-lustria",
  subsets: ["latin"],
  weight: ["400"],
});

// Sans-serif pour le corps de texte et l'interface.
const mulish = Mulish({
  variable: "--font-mulish",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata = {
  title: "Nayaar — Conseiller Olfactif",
  description: "Votre conseiller olfactif personnel, Maison Nayaar.",
  // PWA : icône d'app (Android/Chrome) et icône d'accueil iOS (obligatoirement
  // du PNG pour Safari, pas de SVG). Le manifest (app/manifest.js) référence
  // les mêmes fichiers pour l'installation.
  icons: {
    icon: "/icon-512.png",
    apple: "/apple-touch-icon.png",
  },
  // "Ajouter à l'écran d'accueil" sur iOS Safari (qui ignore le manifest
  // Web standard) : ces balises sont ce qui rend l'app installable et
  // utilisable en plein écran (sans barre d'adresse) sur iPhone.
  appleWebApp: {
    capable: true,
    title: "Nayaar",
    statusBarStyle: "black-translucent",
  },
};

// Couleur de la barre système du navigateur/OS quand l'app est ouverte ou
// installée — alignée sur le fond crème du Header pour une intégration
// visuelle sans rupture de couleur en haut d'écran.
export const viewport = {
  themeColor: "#faf7f2",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="fr"
      className={`${lustria.variable} ${mulish.variable} h-full antialiased`}
    >
      {/* TooltipProvider requis par les composants Prompt Kit (message, scroll-button...) qui utilisent des tooltips */}
      <body className="min-h-full flex flex-col bg-nayaar-cream text-nayaar-ink font-sans">
        <TooltipProvider delayDuration={200}>{children}</TooltipProvider>
        <RegisterServiceWorker />
      </body>
    </html>
  );
}
