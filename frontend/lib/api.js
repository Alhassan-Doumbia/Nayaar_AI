// Appel à l'API FastAPI Nayaar (POST /api/chat).

const URL_API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// L'appel Claude prend quelques secondes (recherche hybride + génération) :
// on laisse une marge large avant de considérer que ça n'aboutira pas.
const DELAI_TIMEOUT_MS = 30000;

/**
 * Envoie un message au chat Nayaar et retourne { reply, perfumes, session_id }.
 * Lève une Error avec un message destiné à être affiché tel quel dans le
 * fil de conversation en cas d'échec (réseau, timeout, ou erreur API).
 *
 * Mode consultation autonome : aucun historique n'est envoyé — chaque appel
 * est une demande indépendante, le backend ne le gère plus (voir
 * backend/app/chat/rag.py).
 *
 * @param {string} message
 * @param {string|null} sessionId
 */
export async function envoyerMessageChat(message, sessionId) {
  const controleur = new AbortController();
  const idTimeout = setTimeout(() => controleur.abort(), DELAI_TIMEOUT_MS);

  let reponse;
  try {
    reponse = await fetch(`${URL_API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
      signal: controleur.signal,
    });
  } catch (erreur) {
    if (erreur.name === "AbortError") {
      throw new Error(
        "La réponse prend plus de temps que prévu. Merci de réessayer dans un instant."
      );
    }
    throw new Error(
      "Impossible de contacter l'assistant Nayaar. Vérifiez que l'API est bien lancée en local."
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
      const corps = await reponse.json();
      detail = corps?.detail ?? "";
    } catch {
      // corps non JSON : on garde le message générique ci-dessous
    }
    throw new Error(
      detail || `L'assistant a rencontré une erreur (code ${reponse.status}).`
    );
  }

  return reponse.json();
}
