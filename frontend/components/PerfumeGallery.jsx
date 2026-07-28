"use client";

import { motion } from "framer-motion";
import { PerfumeImage } from "@/components/PerfumeImage";
import { CopyButton } from "@/components/CopyButton";
import { normaliserScoreAffichage } from "@/lib/score";

// Le parent orchestre le délai entre chaque vignette (effet cascade) ; les
// vignettes elles-mêmes ne définissent que leur propre animation d'entrée.
const conteneurVariants = {
  cache: {},
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

const vignetteVariants = {
  cache: { opacity: 0, y: 10 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: "easeOut" } },
};

/**
 * Rangée horizontale défilante de vignettes parfum, façon galerie de
 * résultats de recherche — pour présenter plusieurs alternatives à la
 * suite les unes des autres. 100% maison.
 *
 * @param {object[]} parfums - liste de { nom, marque, image_url, score_compatibilite }
 */
export function PerfumeGallery({ parfums }) {
  if (!parfums?.length) return null;

  return (
    <motion.div
      initial="cache"
      animate="visible"
      variants={conteneurVariants}
      className="scrollbar-hidden flex w-full gap-3 overflow-x-auto pb-1"
    >
      {parfums.map((parfum) => (
        <motion.article
          key={`${parfum.marque}-${parfum.nom}`}
          variants={vignetteVariants}
          className="flex w-40 shrink-0 flex-col gap-2 rounded-xl border border-nayaar-gold-soft/50 bg-white p-2.5 shadow-sm"
        >
          <PerfumeImage
            src={parfum.image_url}
            nom={parfum.nom}
            className="h-28 w-full rounded-md"
            sizes="160px"
            // Vignettes chargées ensemble (peu nombreuses) : préchargées
            // pour que le défilement horizontal soit fluide dès l'arrivée,
            // plutôt que de charger paresseusement au fil du scroll.
            priority
          />
          <div>
            <p className="label-caps text-[0.6rem] text-nayaar-gold">
              {parfum.marque}
            </p>
            <p className="truncate font-serif text-sm text-nayaar-ink">
              {parfum.nom}
            </p>
            <div className="mt-0.5 flex items-center justify-between gap-1">
              <p className="text-xs text-nayaar-label">
                {normaliserScoreAffichage(parfum.score_compatibilite)}% compatible
              </p>
              {/* Copie "Nom — Marque", discrète, alignée avec le score */}
              <CopyButton
                texte={`${parfum.nom} — ${parfum.marque}`}
                className="h-5 w-5 shrink-0"
              />
            </div>
          </div>
        </motion.article>
      ))}
    </motion.div>
  );
}
