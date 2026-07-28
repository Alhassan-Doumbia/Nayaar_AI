"use client";

import { useState } from "react";
import Image from "next/image";

/**
 * Image d'un parfum avec fallback élégant obligatoire : si l'URL est
 * absente (~9% des parfums de la Knowledge Base) ou si le chargement
 * échoue (onError), on affiche un cadre crème/or avec le nom du parfum en
 * serif — jamais l'icône d'image cassée par défaut du navigateur.
 *
 * `className` définit la TAILLE du conteneur (ex. "h-56 w-full") : l'image
 * et le fallback utilisent tous les deux `fill`/`absolute inset-0` pour
 * remplir exactement ce même conteneur, plutôt que des dimensions en
 * pixels séparées qui pouvaient déborder de la carte/vignette qui les
 * affiche.
 *
 * @param {string} src - Image URL (peut être vide/undefined)
 * @param {string} nom - nom du parfum, utilisé comme alt et comme contenu du fallback
 * @param {string} className - classes de TAILLE du conteneur (h-*, w-*), plus arrondi/bordure éventuels
 * @param {string} [sizes] - attribut `sizes` de next/image (vignette légère vs carte détaillée)
 * @param {boolean} [priority] - précharge l'image (désactive le lazy-loading) ; utilisé pour les
 *   vignettes de PerfumeGallery, affichées ensemble, pour un défilement fluide dès l'apparition
 */
export function PerfumeImage({ src, nom, className = "", sizes = "320px", priority = false }) {
  // On bascule sur le fallback si l'URL est vide dès le départ, ou si
  // next/image signale une erreur de chargement (onError) une fois monté.
  const [enErreur, setEnErreur] = useState(false);
  const afficherFallback = !src || enErreur;

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {afficherFallback ? (
        <div className="absolute inset-0 flex items-center justify-center border border-nayaar-gold-soft bg-nayaar-cream-deep p-4 text-center">
          <span className="font-serif text-sm leading-snug text-nayaar-ink/80">
            {nom}
          </span>
        </div>
      ) : (
        <Image
          src={src}
          alt={nom}
          fill
          sizes={sizes}
          loading={priority ? undefined : "lazy"}
          priority={priority}
          onError={() => setEnErreur(true)}
          className="object-cover"
        />
      )}
    </div>
  );
}
