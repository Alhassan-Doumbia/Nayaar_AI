"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import { PerfumeImage } from "@/components/PerfumeImage";
import { LayeringResults } from "@/components/LayeringResults";
import { Loader } from "@/components/ui/loader";
import { proposerLayering } from "@/lib/api";

/**
 * Panneau latéral de layering : appelle POST /api/layering pour un parfum
 * donné et affiche le guide de superposition (propositions + explication
 * de Claude). C'est une couche par-dessus le chat — il a son propre état
 * local, il ne touche jamais à useChat ni au fil de conversation derrière.
 *
 * Mode consultation autonome, comme le chat : un appel indépendant à
 * chaque ouverture, aucun historique.
 *
 * @param {number|null} perfumeId - id du parfum de référence ; panneau fermé si null/undefined
 * @param {() => void} onClose
 */
export function LayeringPanel({ perfumeId, onClose }) {
  const estOuvert = perfumeId !== null && perfumeId !== undefined;

  const [donnees, setDonnees] = useState(null);
  const [erreur, setErreur] = useState(null);
  const [chargement, setChargement] = useState(false);

  // Relance l'appel à chaque nouvelle ouverture (ou changement de parfum
  // de référence, si le panneau reste monté d'un clic à l'autre).
  useEffect(() => {
    if (!estOuvert) return;

    let annule = false;
    setDonnees(null);
    setErreur(null);
    setChargement(true);

    proposerLayering(perfumeId)
      .then((reponse) => {
        if (!annule) setDonnees(reponse);
      })
      .catch((erreurAppel) => {
        if (!annule) {
          setErreur(
            erreurAppel.message || "Une erreur est survenue. Merci de réessayer."
          );
        }
      })
      .finally(() => {
        if (!annule) setChargement(false);
      });

    return () => {
      annule = true; // évite d'appliquer une réponse tardive si le panneau a été refermé entre-temps
    };
  }, [perfumeId, estOuvert]);

  return (
    <AnimatePresence>
      {estOuvert && (
        <>
          {/* Fond assombri : un clic dessus ferme le panneau, sans toucher au chat derrière */}
          <motion.div
            key="layering-fond"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            onClick={onClose}
            className="fixed inset-0 z-40 bg-nayaar-black/50"
          />

          {/* Volet latéral, glisse depuis la droite */}
          <motion.aside
            key="layering-panneau"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            // Mobile : plein écran (w-full, pas de plafond). Ordinateur
            // (>= 768px) : plafonné à 750px (+300px par rapport aux 450px
            // précédents), plus confortable pour lire le guide et les
            // cartes côte à côte sans paraître écrasé.
            className="fixed top-0 right-0 z-50 flex h-full w-full flex-col bg-nayaar-cream shadow-2xl md:max-w-187.5"
          >
            {/* En-tête : rappel du parfum de base */}
            <header className="flex items-center gap-3 border-b border-nayaar-gold-soft/40 px-5 py-4">
              {donnees && (
                <PerfumeImage
                  src={donnees.parfum_reference.image_url}
                  nom={donnees.parfum_reference.nom}
                  className="h-12 w-12 shrink-0 rounded-full"
                  sizes="48px"
                />
              )}
              <div className="min-w-0 flex-1">
                <p className="label-caps">Guide de superposition</p>
                {donnees && (
                  <p className="truncate font-serif text-sm text-nayaar-ink">
                    {donnees.parfum_reference.nom} — {donnees.parfum_reference.marque}
                  </p>
                )}
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Fermer le panneau de layering"
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-nayaar-label transition-colors hover:bg-nayaar-cream-deep hover:text-nayaar-gold"
              >
                <X className="h-4 w-4" />
              </button>
            </header>

            {/* Contenu défilant */}
            <div className="flex-1 overflow-y-auto px-5 py-5">
              {chargement && (
                <div className="flex h-full items-center justify-center">
                  <Loader variant="typing" size="md" />
                </div>
              )}

              {erreur && !chargement && (
                <p className="text-sm italic text-nayaar-ink/70">{erreur}</p>
              )}

              {donnees && !chargement && !erreur && (
                <LayeringResults perfumes={donnees.perfumes} reply={donnees.reply} />
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
