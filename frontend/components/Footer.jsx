/**
 * Pied de page discret : simple mention de la maison, en petites capitales
 * espacées (même traitement que les labels "ASSISTANT" / "VOUS").
 */
export function Footer() {
  return (
    <footer className="border-t border-nayaar-gold-soft/40 bg-nayaar-cream-deep py-4 text-center">
      <p className="label-caps">Expérience artisanale par Nayaar</p>
    </footer>
  );
}
