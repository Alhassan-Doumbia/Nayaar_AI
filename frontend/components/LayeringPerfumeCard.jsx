"use client";

import { motion } from "framer-motion";
import { PerfumeImage } from "@/components/PerfumeImage";
import { CopyButton } from "@/components/CopyButton";
import { normaliserScoreAffichage } from "@/lib/score";

// Libellé affiché pour chaque rôle — cohérent avec le vocabulaire du guide
// rédigé par Claude ("base" / "dessus", voir layering_system_prompt.py).
const LIBELLE_ROLE = {
  base: "Base",
  dessus: "En surface",
};

/**
 * Carte d'un parfum proposé en superposition (panneau de layering) :
 * même langage visuel que PerfumeCard/PerfumeGallery (image avec fallback,
 * marque en petites capitales dorées, nom en serif, score animé, bouton
 * copier), avec en plus un badge indiquant le rôle suggéré dans
 * l'application (base ou dessus).
 *
 * @param {object} parfum - { nom, marque, image_url, score_compatibilite, details, role }
 */
export function LayeringPerfumeCard({ parfum }) {
  const pourcentage = normaliserScoreAffichage(parfum.score_compatibilite);

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="flex gap-3 overflow-hidden rounded-xl border border-nayaar-gold-soft/50 bg-white p-3 shadow-sm"
    >
      <div className="relative shrink-0">
        <PerfumeImage
          src={parfum.image_url}
          nom={parfum.nom}
          className="h-20 w-20 rounded-lg"
          sizes="80px"
        />
        {/* Badge de rôle : indication visuelle de l'ordre d'application (base d'abord, dessus ensuite) */}
        <span className="absolute -top-1.5 -left-1.5 rounded-full bg-nayaar-black px-2 py-0.5 text-[0.6rem] font-medium uppercase tracking-wide text-nayaar-cream">
          {LIBELLE_ROLE[parfum.role]}
        </span>
      </div>

      <div className="flex min-w-0 flex-1 flex-col justify-center gap-1.5">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="label-caps text-nayaar-gold">{parfum.marque}</p>
            <p className="truncate font-serif text-base text-nayaar-ink">
              {parfum.nom}
            </p>
          </div>
          <CopyButton
            texte={`${parfum.nom} — ${parfum.marque}`}
            className="h-6 w-6 shrink-0"
          />
        </div>

        <div>
          <div className="mb-1 flex items-baseline justify-between">
            <span className="text-[0.65rem] text-nayaar-label">Compatibilité</span>
            <span className="text-xs font-medium text-nayaar-gold">{pourcentage}%</span>
          </div>
          <div className="h-1 w-full overflow-hidden rounded-full bg-nayaar-cream-deep">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pourcentage}%` }}
              transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
              className="h-full rounded-full bg-nayaar-gold"
            />
          </div>
        </div>
      </div>
    </motion.article>
  );
}
