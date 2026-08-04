"use client";

import { motion } from "framer-motion";
import { Trash2 } from "lucide-react";
import { PerfumeImage } from "@/components/PerfumeImage";

/**
 * Une entrée de l'historique "Mes layerings" (sauvegardé en localStorage) :
 * cliquer dessus réaffiche le layering sans relancer d'appel API (les
 * données sont déjà dans l'enregistrement), le bouton corbeille supprime
 * l'entrée.
 *
 * @param {object} entree - { id, parfum_de_base, date, ... } (voir lib/layeringStorage.js)
 * @param {() => void} onSelect
 * @param {() => void} onDelete
 */
export function LayeringHistoryEntry({ entree, onSelect, onDelete }) {
  const dateFormatee = new Date(entree.date).toLocaleDateString("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <motion.li
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex items-center gap-3 rounded-xl border border-nayaar-gold-soft/50 bg-white p-3 shadow-sm"
    >
      <button
        type="button"
        onClick={onSelect}
        className="flex min-w-0 flex-1 items-center gap-3 text-left"
      >
        <PerfumeImage
          src={entree.parfum_de_base.image_url}
          nom={entree.parfum_de_base.nom}
          className="h-12 w-12 shrink-0 rounded-lg"
          sizes="48px"
        />
        <span className="min-w-0">
          <span className="block truncate font-serif text-sm text-nayaar-ink">
            {entree.parfum_de_base.nom}
          </span>
          <span className="block truncate text-xs text-nayaar-label">
            {entree.parfum_de_base.marque} · {dateFormatee}
          </span>
        </span>
      </button>

      <button
        type="button"
        onClick={onDelete}
        aria-label="Supprimer ce layering sauvegardé"
        title="Supprimer"
        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-nayaar-label transition-colors hover:bg-nayaar-cream-deep hover:text-nayaar-gold"
      >
        <Trash2 className="h-4 w-4" />
      </button>
    </motion.li>
  );
}
