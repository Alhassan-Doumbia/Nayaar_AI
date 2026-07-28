import { Inter, Playfair_Display } from "next/font/google";
import { TooltipProvider } from "@/components/ui/tooltip";
import "./globals.css";

// Serif élégante pour le logo « NAYAAR. » et les titres.
const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["500", "600"],
});

// Sans-serif lisible pour le corps de texte et l'interface.
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata = {
  title: "Nayaar — Conseiller Olfactif",
  description: "L'assistant olfactif intelligent de Maison Nayaar.",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="fr"
      className={`${playfair.variable} ${inter.variable} h-full antialiased`}
    >
      {/* TooltipProvider requis par les composants Prompt Kit (message, scroll-button...) qui utilisent des tooltips */}
      <body className="min-h-full flex flex-col bg-nayaar-cream text-nayaar-ink font-sans">
        <TooltipProvider delayDuration={200}>{children}</TooltipProvider>
      </body>
    </html>
  );
}
