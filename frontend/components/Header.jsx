/**
 * En-tête de l'application : logo "NAYAAR." en serif très espacé, avec le
 * point du logo en doré (accent de la maison). Sobre, pas de navigation
 * superflue — l'expérience reste centrée sur le contenu.
 *
 * `nav` (optionnel) : un élément de navigation (ex. lien de retour, lien
 * vers une autre page) affiché discrètement à gauche, sans perturber le
 * centrage du logo. Absent par défaut => rendu identique à avant.
 */
export function Header({ nav }) {
  return (
    <header className="relative flex items-center justify-center border-b border-nayaar-gold-soft/40 bg-nayaar-cream py-6">
      {nav && <div className="absolute left-4 sm:left-6">{nav}</div>}
      <h1 className="select-none font-serif text-2xl font-medium tracking-[0.35em] text-nayaar-ink">
        NAYAAR<span className="text-nayaar-gold">.</span>
      </h1>
    </header>
  );
}
