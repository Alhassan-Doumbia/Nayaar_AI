/**
 * En-tête de l'application : logo "NAYAAR." en serif très espacé, avec le
 * point du logo en doré (accent de la maison). Sobre, pas de navigation
 * superflue — l'expérience est entièrement conversationnelle.
 */
export function Header() {
  return (
    <header className="flex items-center justify-center border-b border-nayaar-gold-soft/40 bg-nayaar-cream py-6">
      <h1 className="select-none font-serif text-2xl font-medium tracking-[0.35em] text-nayaar-ink">
        NAYAAR<span className="text-nayaar-gold">.</span>
      </h1>
    </header>
  );
}
