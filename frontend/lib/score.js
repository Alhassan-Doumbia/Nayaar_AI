// Normalisation d'affichage du score de compatibilité.
//
// Le score brut renvoyé par le moteur (backend/app/recommendation/scoring.py
// et hybrid.py) est une moyenne pondérée de composantes indépendantes : il
// se retrouve presque toujours dans une fourchette resserrée (~0.3 à 0.9 en
// pratique, souvent 0.4-0.6), qui afficherait mal en pourcentage brut
// ("52% de compatibilité" n'inspire pas confiance). On étire cette
// fourchette réelle vers une fourchette d'affichage plus premium (65-99%),
// SANS jamais modifier ni renvoyer le score brut au backend — c'est une
// reformulation d'affichage uniquement, la logique de tri reste sur le
// score réel.
const PLAGE_SCORE_BRUT = { min: 0.3, max: 0.9 };
const PLAGE_AFFICHAGE = { min: 65, max: 99 };

/**
 * Convertit un score brut (0-1) en pourcentage crédible pour l'affichage.
 * @param {number} scoreBrut
 * @returns {number} entier entre PLAGE_AFFICHAGE.min et PLAGE_AFFICHAGE.max
 */
export function normaliserScoreAffichage(scoreBrut) {
  const borne = Math.min(
    Math.max(scoreBrut, PLAGE_SCORE_BRUT.min),
    PLAGE_SCORE_BRUT.max
  );
  const ratio =
    (borne - PLAGE_SCORE_BRUT.min) /
    (PLAGE_SCORE_BRUT.max - PLAGE_SCORE_BRUT.min);

  return Math.round(
    PLAGE_AFFICHAGE.min + ratio * (PLAGE_AFFICHAGE.max - PLAGE_AFFICHAGE.min)
  );
}
