// Appels à l'API FastAPI Nayaar (POST /api/chat, POST /api/layering).

const URL_API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Les appels Claude prennent quelques secondes (recherche + génération) :
// on laisse une marge large avant de considérer que ça n'aboutira pas.
const DELAI_TIMEOUT_MS = 30000;

/**
 * Fonction interne partagée : POST JSON vers l'API avec timeout, et lève
 * une Error avec un message déjà prêt à afficher tel quel dans l'interface
 * en cas d'échec (réseau, timeout, ou erreur renvoyée par l'API).
 */
async function _poster(chemin, corps) {
  const controleur = new AbortController();
  const idTimeout = setTimeout(() => controleur.abort(), DELAI_TIMEOUT_MS);

  let reponse;
  try {
    reponse = await fetch(`${URL_API}${chemin}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(corps),
      signal: controleur.signal,
    });
  } catch (erreur) {
    if (erreur.name === "AbortError") {
      throw new Error(
        "La réponse prend plus de temps que prévu. Merci de réessayer dans un instant."
      );
    }
    throw new Error(
      "Le réseau semble hésiter — l'assistant Nayaar ne répond pas. Vérifiez que l'API est bien lancée en local."
    );
  } finally {
    clearTimeout(idTimeout);
  }

  if (!reponse.ok) {
    // L'API renvoie {"detail": "..."} sur les erreurs gérées (voir main.py) ;
    // on essaie de le récupérer pour un message plus précis, sans jamais
    // planter si le corps n'est pas du JSON exploitable.
    let detail = "";
    try {
      const corpsErreur = await reponse.json();
      detail = corpsErreur?.detail ?? "";
    } catch {
      // corps non JSON : on garde le message générique ci-dessous
    }
    throw new Error(
      detail || `L'assistant n'a pas pu répondre cette fois (code ${reponse.status}).`
    );
  }

  return reponse.json();
}

/**
 * Envoie un message au chat Nayaar et retourne { reply, perfumes, session_id }.
 *
 * Mode consultation autonome : aucun historique n'est envoyé — chaque appel
 * est une demande indépendante, le backend ne le gère plus (voir
 * backend/app/chat/rag.py).
 *
 * @param {string} message
 * @param {string|null} sessionId
 */
export function envoyerMessageChat(message, sessionId) {
  return _poster("/api/chat", { message, session_id: sessionId });
}

/**
 * Demande un guide de superposition (layering) pour un parfum donné et
 * retourne { reply, parfum_reference, perfumes }. Mode consultation
 * autonome également : aucun historique, chaque appel est indépendant.
 *
 * @param {number} perfumeId - id du parfum de référence (position dans la Knowledge Base)
 * @param {number} [n] - nombre de propositions souhaitées
 */
export function proposerLayering(perfumeId, n = 3) {
  return _poster("/api/layering", { perfume_id: perfumeId, n });
}

/**
 * Recherche textuelle simple par nom/marque (GET /api/search), pour
 * l'autocomplétion de la page layering. Pas de timeout dédié : c'est un
 * appel léger et fréquent (debounce côté appelant) — en cas d'échec, on
 * retourne simplement une liste vide plutôt que de casser la saisie de
 * l'utilisateur avec un message d'erreur intrusif.
 *
 * @param {string} texte
 * @returns {Promise<{id:number, nom:string, marque:string, image_url:string}[]>}
 */
export async function rechercherParNom(texte) {
  try {
    const url = new URL(`${URL_API}/api/search`);
    url.searchParams.set("q", texte);
    const reponse = await fetch(url.toString());
    if (!reponse.ok) return [];
    return await reponse.json();
  } catch {
    return [];
  }
}
