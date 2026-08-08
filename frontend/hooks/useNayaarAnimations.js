"use client";

import { useEffect } from "react";
import gsap from "gsap";

/**
 * Anime le liseré doré au focus d'un élément (ex. zone de saisie) : un
 * trait qui se dessine lentement de gauche à droite plutôt que d'apparaître
 * brutalement — le luxe est calme (voir Docs/NAYAAR_DESIGN_DIRECTION.md,
 * section 7 "Animations").
 *
 * @param {React.RefObject<HTMLElement>} liseréRef - élément à animer (ex. une div `::after` scaleX)
 * @param {boolean} actif - déclenche l'animation quand il passe à true
 */
export function useLisereDoreAuFocus(liseréRef, actif) {
  useEffect(() => {
    if (!liseréRef.current) return;

    gsap.to(liseréRef.current, {
      scaleX: actif ? 1 : 0,
      duration: 0.4,
      ease: "power2.out",
    });
  }, [actif, liseréRef]);
}
