"use client";

import { motion } from "framer-motion";
import { PerfumeImage } from "@/components/PerfumeImage";
import { CopyButton } from "@/components/CopyButton";
import { normaliserScoreAffichage } from "@/lib/score";

/**
 * Carte verticale détaillée pour LA recommandation principale d'un tour de
 * conversation : image, marque (petites capitales dorées), nom (serif),
 * notes principales (puces), barre de score de compatibilité animée.
 * 100% maison (pas de composant Prompt Kit sous-jacent).
 *
 * @param {object} parfum - { nom, marque, image_url, notes_principales, score_compatibilite, concentration }
 */
export function PerfumeCard({ parfum }) {
  // Le score brut du moteur (souvent 0.4-0.6) est reformulé en pourcentage
  // crédible pour l'affichage — voir lib/score.js pour le détail.
  const pourcentage = normaliserScoreAffichage(parfum.score_compatibilite);

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut", delay: 0.15 }}
      className="w-full max-w-xs overflow-hidden rounded-2xl border border-nayaar-gold-soft/60 bg-white shadow-sm"
    >
      <PerfumeImage
        src={parfum.image_url}
        nom={parfum.nom}
        className="h-56 w-full"
        sizes="(max-width: 640px) 100vw, 320px"
      />

      <div className="flex flex-col gap-3 p-5">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="label-caps text-nayaar-gold">{parfum.marque}</p>
            <h3 className="mt-1 font-serif text-xl text-nayaar-ink">
              {parfum.nom}
            </h3>
            {parfum.concentration && (
              <p className="text-xs text-nayaar-label">{parfum.concentration}</p>
            )}
          </div>

          {/* Copie "Nom — Marque" : plus utile qu'un nom seul pour une recherche externe */}
          <CopyButton
            texte={`${parfum.nom} — ${parfum.marque}`}
            className="mt-1 h-7 w-7 shrink-0"
          />
        </div>

        {parfum.notes_principales?.length > 0 && (
          <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-nayaar-ink/80">
            {parfum.notes_principales.map((note) => (
              <li key={note} className="flex items-center gap-1.5">
                <span className="h-1 w-1 rounded-full bg-nayaar-gold" />
                {note}
              </li>
            ))}
          </ul>
        )}

        {/* Score de compatibilité : barre animée de 0 jusqu'à sa valeur */}
        <div className="mt-1">
          <div className="mb-1.5 flex items-baseline justify-between">
            <span className="label-caps">Compatibilité</span>
            <span className="font-serif text-lg text-nayaar-gold">
              {pourcentage}%
            </span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-nayaar-cream-deep">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pourcentage}%` }}
              transition={{ duration: 0.9, ease: "easeOut", delay: 0.3 }}
              className="h-full rounded-full bg-nayaar-gold"
            />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
