"use client";

import { motion } from "framer-motion";
import { Layers } from "lucide-react";
import { PerfumeImage } from "@/components/PerfumeImage";
import { CopyButton } from "@/components/CopyButton";
import { normaliserScoreAffichage } from "@/lib/score";

// Deux variantes, voir Docs/NAYAAR_DESIGN_DIRECTION.md section 5 :
// - "sombre" (par défaut) : la fiche vit À L'INTÉRIEUR de la bulle noire de
//   l'assistant — carte translucide claire sur fond sombre, marque dorée,
//   nom en crème clair. C'est là que le luxe se voit le plus.
// - "claire" : variante hors bulle (fond crème), pour un contexte où la
//   fiche est affichée seule (ex. galerie d'alternatives autonome).
const STYLES_VARIANTE = {
  sombre: {
    carte: "border border-nayaar-on-dark-border bg-nayaar-on-dark-surface",
    marque: "text-nayaar-gold",
    nom: "text-[#F5F0E8]",
    concentration: "text-nayaar-assistant-muted",
    note: "text-nayaar-assistant-muted",
    pastille: "bg-nayaar-assistant-accent",
    labelScore: "text-nayaar-assistant-muted",
    valeurScore: "text-nayaar-assistant-accent",
    pisteScore: "bg-white/10",
    remplissageScore: "bg-nayaar-assistant-accent",
    bouton:
      "border-nayaar-on-dark-border text-nayaar-assistant-muted hover:border-nayaar-assistant-accent hover:bg-white/5",
  },
  claire: {
    carte: "border border-nayaar-gold-soft bg-white shadow-[0_1px_3px_rgba(28,25,23,0.06)]",
    marque: "text-nayaar-gold",
    nom: "text-nayaar-ink",
    concentration: "text-nayaar-label",
    note: "text-nayaar-ink/80",
    pastille: "bg-nayaar-gold",
    labelScore: "",
    valeurScore: "text-nayaar-gold",
    pisteScore: "bg-nayaar-cream-deep",
    remplissageScore: "bg-nayaar-gold",
    bouton:
      "border-nayaar-gold-soft text-nayaar-ink hover:border-nayaar-gold hover:bg-nayaar-cream-deep",
  },
};

/**
 * Carte verticale détaillée pour LA recommandation principale d'un tour de
 * conversation : image, marque (petites capitales dorées), nom (serif),
 * notes principales (puces), barre de score de compatibilité animée.
 * 100% maison (pas de composant Prompt Kit sous-jacent).
 *
 * @param {object} parfum - { id, nom, marque, image_url, notes_principales, score_compatibilite, concentration }
 * @param {(perfumeId: number) => void} [onOpenLayering] - ouvre le panneau de layering pour ce parfum ; le bouton n'apparaît que si fourni (et que parfum.id est connu)
 * @param {"sombre"|"claire"} [variante] - "sombre" (défaut) pour un affichage dans la bulle assistant
 */
export function PerfumeCard({ parfum, onOpenLayering, variante = "sombre" }) {
  // Le score brut du moteur (souvent 0.4-0.6) est reformulé en pourcentage
  // crédible pour l'affichage — voir lib/score.js pour le détail.
  const pourcentage = normaliserScoreAffichage(parfum.score_compatibilite);
  const style = STYLES_VARIANTE[variante];

  return (
    <motion.article
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut", delay: 0.15 }}
      className={`w-full max-w-xs overflow-hidden rounded-lg ${style.carte}`}
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
            <p className={`label-caps ${style.marque}`}>{parfum.marque}</p>
            <h3 className={`mt-1 font-serif text-xl ${style.nom}`}>
              {parfum.nom}
            </h3>
            {parfum.concentration && (
              <p className={`text-xs ${style.concentration}`}>{parfum.concentration}</p>
            )}
          </div>

          {/* Copie "Nom — Marque" : plus utile qu'un nom seul pour une recherche externe */}
          <CopyButton
            texte={`${parfum.nom} — ${parfum.marque}`}
            className="mt-1 h-7 w-7 shrink-0"
          />
        </div>

        {parfum.notes_principales?.length > 0 && (
          <ul className={`flex flex-wrap gap-x-4 gap-y-1 text-sm ${style.note}`}>
            {parfum.notes_principales.map((note) => (
              <li key={note} className="flex items-center gap-1.5">
                <span className={`h-1 w-1 rounded-full ${style.pastille}`} />
                {note}
              </li>
            ))}
          </ul>
        )}

        {/* Score de compatibilité : barre animée de 0 jusqu'à sa valeur */}
        <div className="mt-1">
          <div className="mb-1.5 flex items-baseline justify-between">
            <span className={`label-caps ${style.labelScore}`}>Compatibilité</span>
            <span className={`font-serif text-lg ${style.valeurScore}`}>
              {pourcentage}%
            </span>
          </div>
          <div className={`h-1.5 w-full overflow-hidden rounded-full ${style.pisteScore}`}>
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pourcentage}%` }}
              transition={{ duration: 0.9, ease: "easeOut", delay: 0.3 }}
              className={`h-full rounded-full ${style.remplissageScore}`}
            />
          </div>
        </div>

        {/* Entrée vers le panneau de layering dédié (remplace l'ancien chip
            désactivé "Suggérer un layering" : le layering est maintenant
            actif, contextuel à CE parfum précis). */}
        {onOpenLayering && parfum.id != null && (
          <button
            type="button"
            onClick={() => onOpenLayering(parfum.id)}
            className={`mt-1 flex items-center justify-center gap-2 rounded-full border px-4 py-2 text-xs font-medium tracking-wide uppercase transition-colors ${style.bouton}`}
          >
            <Layers className="h-3.5 w-3.5" />
            Proposer un layering
          </button>
        )}
      </div>
    </motion.article>
  );
}
