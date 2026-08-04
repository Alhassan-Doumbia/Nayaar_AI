// Persistance des layerings générés, dans localStorage (pas de backend de
// stockage : le client doit pouvoir retrouver ses recommandations après
// fermeture du navigateur, sur cet appareil). Un seul module centralise
// toute la lecture/écriture, pour ne jamais dupliquer la logique de
// robustesse (JSON corrompu, clé absente) ailleurs dans l'app.

const CLE_LOCALSTORAGE = "nayaar_layerings";

function genererId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return `layering-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/**
 * Vérifie qu'un enregistrement a bien la forme attendue avant de l'exposer
 * au reste de l'app — une entrée partiellement corrompue (ex. localStorage
 * modifié à la main, ancienne version du format) est silencieusement
 * écartée plutôt que de faire planter l'affichage de l'historique.
 */
function estEnregistrementValide(entree) {
  return Boolean(
    entree &&
      typeof entree === "object" &&
      entree.id &&
      entree.parfum_de_base &&
      Array.isArray(entree.propositions) &&
      typeof entree.guide === "string" &&
      entree.date
  );
}

/**
 * Retourne la liste des layerings sauvegardés (plus récent en premier).
 * Ne lève jamais d'exception : localStorage absent (rendu serveur), clé
 * jamais créée (première visite), ou JSON corrompu retournent tous []
 * plutôt qu'une erreur.
 */
export function obtenirLayeringsSauvegardes() {
  if (typeof window === "undefined") return [];

  const brut = window.localStorage.getItem(CLE_LOCALSTORAGE);
  if (!brut) return [];

  try {
    const donnees = JSON.parse(brut);
    if (!Array.isArray(donnees)) return [];
    return donnees.filter(estEnregistrementValide);
  } catch {
    // JSON invalide (fichier corrompu/tronqué) : on repart d'une liste
    // vide plutôt que de casser toute la page.
    return [];
  }
}

/**
 * Sauvegarde un nouveau layering généré (ajouté en tête de liste) et
 * retourne la liste à jour, pour que l'appelant puisse mettre à jour son
 * état React sans relire localStorage juste après.
 *
 * @param {{parfumDeBase: object, propositions: object[], guide: string}} donnees
 */
export function sauvegarderLayering({ parfumDeBase, propositions, guide }) {
  const enregistrement = {
    id: genererId(),
    parfum_de_base: parfumDeBase,
    propositions,
    guide,
    date: new Date().toISOString(),
  };

  const liste = [enregistrement, ...obtenirLayeringsSauvegardes()];
  window.localStorage.setItem(CLE_LOCALSTORAGE, JSON.stringify(liste));
  return liste;
}

/** Supprime un layering sauvegardé par id et retourne la liste à jour. */
export function supprimerLayering(id) {
  const liste = obtenirLayeringsSauvegardes().filter((entree) => entree.id !== id);
  window.localStorage.setItem(CLE_LOCALSTORAGE, JSON.stringify(liste));
  return liste;
}
