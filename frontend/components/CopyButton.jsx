"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Check, Copy } from "lucide-react";

// Durée d'affichage de la confirmation ("Copié") avant de revenir à l'icône
// de copie normale.
const DUREE_CONFIRMATION_MS = 1500;

/**
 * Petit bouton discret qui copie du texte dans le presse-papiers (API
 * Clipboard du navigateur), avec un retour visuel bref (icône coche
 * pendant ~1,5s, micro-animation en fondu). Utilisé sur PerfumeCard et sur
 * les vignettes de PerfumeGallery pour copier "Nom — Marque" du parfum.
 *
 * @param {string} texte - le texte à copier
 * @param {string} [className] - classes supplémentaires (positionnement, taille)
 */
export function CopyButton({ texte, className = "" }) {
  const [copie, setCopie] = useState(false);

  const copier = async (evenement) => {
    // Empêche le clic de se propager à des éléments cliquables englobants
    // (ex. la carte elle-même, si elle devient cliquable plus tard).
    evenement.stopPropagation();
    try {
      await navigator.clipboard.writeText(texte);
      setCopie(true);
      setTimeout(() => setCopie(false), DUREE_CONFIRMATION_MS);
    } catch {
      // Presse-papiers indisponible (contexte non sécurisé, permission
      // refusée...) : on n'affiche pas d'erreur intrusive, le bouton reste
      // simplement sans effet visible plutôt que de casser l'interface.
    }
  };

  return (
    <button
      type="button"
      onClick={copier}
      aria-label={copie ? "Nom copié" : "Copier le nom du parfum"}
      title={copie ? "Copié" : "Copier le nom"}
      className={`flex items-center justify-center rounded-full text-nayaar-label transition-colors hover:text-nayaar-gold ${className}`}
    >
      <AnimatePresence mode="wait" initial={false}>
        {copie ? (
          <motion.span
            key="coche"
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.7 }}
            transition={{ duration: 0.15 }}
            className="flex items-center gap-1 text-nayaar-gold"
          >
            <Check className="h-3.5 w-3.5" />
          </motion.span>
        ) : (
          <motion.span
            key="copier"
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.7 }}
            transition={{ duration: 0.15 }}
          >
            <Copy className="h-3.5 w-3.5" />
          </motion.span>
        )}
      </AnimatePresence>
    </button>
  );
}
