"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { PerfumeImage } from "@/components/PerfumeImage";
import { rechercherParNom } from "@/lib/api";

const DELAI_DEBOUNCE_MS = 300;
const LONGUEUR_MINIMALE = 2; // évite d'interroger l'API pour 1 caractère isolé

/**
 * Champ de recherche avec autocomplétion : recherche textuelle (nom/marque)
 * via GET /api/search, débouncée pour ne pas spammer l'API à chaque
 * frappe. Affiche les correspondances dans une liste déroulante (image,
 * nom, marque) ; sélectionner une entrée appelle onSelect et referme la liste.
 *
 * @param {(parfum: {id:number, nom:string, marque:string, image_url:string}) => void} onSelect
 */
export function PerfumeSearchInput({ onSelect }) {
  const [texte, setTexte] = useState("");
  const [resultats, setResultats] = useState([]);
  const [listeVisible, setListeVisible] = useState(false);
  const [recherecheEnCours, setRechercheEnCours] = useState(false);
  const idDebounce = useRef(null);

  // Débounce : on ne lance la recherche que DELAI_DEBOUNCE_MS après la
  // dernière frappe, en annulant le délai précédent à chaque nouvelle
  // touche — sans ça, chaque caractère tapé déclencherait un appel API.
  useEffect(() => {
    clearTimeout(idDebounce.current);

    const texteNettoye = texte.trim();
    if (texteNettoye.length < LONGUEUR_MINIMALE) {
      setResultats([]);
      setRechercheEnCours(false);
      return;
    }

    setRechercheEnCours(true);
    idDebounce.current = setTimeout(async () => {
      const reponse = await rechercherParNom(texteNettoye);
      setResultats(reponse);
      setRechercheEnCours(false);
      setListeVisible(true);
    }, DELAI_DEBOUNCE_MS);

    return () => clearTimeout(idDebounce.current);
  }, [texte]);

  const selectionner = (parfum) => {
    setTexte(`${parfum.nom} — ${parfum.marque}`);
    setListeVisible(false);
    setResultats([]);
    onSelect(parfum);
  };

  return (
    <div className="relative w-full">
      <div className="relative">
        <Search className="pointer-events-none absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-nayaar-label" />
        <Input
          value={texte}
          onChange={(evenement) => setTexte(evenement.target.value)}
          onFocus={() => resultats.length > 0 && setListeVisible(true)}
          // laisse le temps au clic sur un résultat de se déclencher avant de fermer la liste
          onBlur={() => setTimeout(() => setListeVisible(false), 150)}
          placeholder="Un parfum de votre coffret…"
          className="h-12 rounded-full border-nayaar-gold-soft bg-white pl-10 text-sm focus-visible:border-nayaar-gold focus-visible:ring-nayaar-gold/30"
        />
      </div>

      <AnimatePresence>
        {listeVisible && texte.trim().length >= LONGUEUR_MINIMALE && (
          <motion.ul
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="absolute z-20 mt-2 max-h-80 w-full overflow-y-auto rounded-xl border border-nayaar-gold-soft/50 bg-white shadow-lg"
          >
            {recherecheEnCours && (
              <li className="px-4 py-3 text-sm text-nayaar-label">Recherche…</li>
            )}

            {!recherecheEnCours && resultats.length === 0 && (
              <li className="px-4 py-3 text-sm text-nayaar-label">
                Aucun parfum trouvé pour « {texte.trim()} ».
              </li>
            )}

            {!recherecheEnCours &&
              resultats.map((parfum) => (
                <li key={parfum.id}>
                  <button
                    type="button"
                    // onMouseDown (pas onClick) : se déclenche AVANT le onBlur de
                    // l'input, sinon la liste se ferme avant que le clic n'aboutisse
                    onMouseDown={() => selectionner(parfum)}
                    className="flex w-full items-center gap-3 px-3 py-2 text-left transition-colors hover:bg-nayaar-cream-deep"
                  >
                    <PerfumeImage
                      src={parfum.image_url}
                      nom={parfum.nom}
                      className="h-10 w-10 shrink-0 rounded-md"
                      sizes="40px"
                    />
                    <span className="min-w-0">
                      <span className="block truncate font-serif text-sm text-nayaar-ink">
                        {parfum.nom}
                      </span>
                      <span className="label-caps block truncate text-[0.6rem] text-nayaar-gold">
                        {parfum.marque}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  );
}
