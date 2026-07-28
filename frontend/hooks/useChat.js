"use client";

import { useCallback, useEffect, useState } from "react";
import { envoyerMessageChat } from "@/lib/api";
import { definirCookie, obtenirCookie } from "@/lib/cookies";

const NOM_COOKIE_SESSION = "nayaar_session_id";
const DUREE_COOKIE_JOURS = 30;

function genererIdSession() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Filet de sécurité pour d'anciens navigateurs sans crypto.randomUUID.
  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

/**
 * Hook de gestion du chat Nayaar.
 *
 * Expose :
 * - messages : liste des tours de conversation, chacun avec un `statut`
 *   ("loading" pendant l'appel API, "streaming" pendant la révélation
 *   progressive du texte, "done" une fois affiché, "error" en cas d'échec)
 * - isLoading : true tant que l'appel API à /api/chat est en cours
 * - sendMessage(texte) : envoie un message utilisateur
 * - marquerMessageTermine(id) : à appeler quand l'animation de streaming
 *   d'un message se termine (voir ResponseStream.onComplete)
 *
 * Mode consultation autonome : chaque sendMessage() est une demande
 * indépendante, aucun historique n'est envoyé à l'API (voir lib/api.js et
 * backend/app/chat/rag.py). Le fil affiché à l'écran garde néanmoins la
 * trace visuelle des échanges précédents pour l'utilisateur — c'est un
 * historique d'AFFICHAGE uniquement, jamais transmis au backend.
 *
 * La session est persistée via cookie (jamais localStorage, cf. consigne),
 * générée une seule fois puis réutilisée tant que le cookie n'expire pas.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    const existant = obtenirCookie(NOM_COOKIE_SESSION);
    if (existant) {
      setSessionId(existant);
      return;
    }
    const nouveau = genererIdSession();
    definirCookie(NOM_COOKIE_SESSION, nouveau, DUREE_COOKIE_JOURS);
    setSessionId(nouveau);
  }, []);

  const sendMessage = useCallback(
    async (texte) => {
      const texteNettoye = texte.trim();
      if (!texteNettoye || isLoading) return;

      const idAssistant = `assistant-${Date.now()}`;

      setMessages((precedent) => [
        ...precedent,
        {
          id: `user-${Date.now()}`,
          role: "user",
          contenu: texteNettoye,
          statut: "done",
        },
        {
          id: idAssistant,
          role: "assistant",
          contenu: "",
          statut: "loading",
          perfumes: [],
        },
      ]);
      setIsLoading(true);

      try {
        const reponse = await envoyerMessageChat(texteNettoye, sessionId);

        setMessages((precedent) =>
          precedent.map((m) =>
            m.id === idAssistant
              ? {
                  ...m,
                  contenu: reponse.reply,
                  statut: "streaming",
                  perfumes: reponse.perfumes || [],
                }
              : m
          )
        );

        // Si le backend attribue un session_id différent (ex. tout premier
        // appel sans session_id fourni), on aligne le cookie dessus.
        if (reponse.session_id && reponse.session_id !== sessionId) {
          definirCookie(NOM_COOKIE_SESSION, reponse.session_id, DUREE_COOKIE_JOURS);
          setSessionId(reponse.session_id);
        }
      } catch (erreur) {
        setMessages((precedent) =>
          precedent.map((m) =>
            m.id === idAssistant
              ? {
                  ...m,
                  statut: "error",
                  contenu:
                    erreur.message ||
                    "Une erreur est survenue. Merci de réessayer dans un instant.",
                }
              : m
          )
        );
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, sessionId]
  );

  const marquerMessageTermine = useCallback((idMessage) => {
    setMessages((precedent) =>
      precedent.map((m) =>
        m.id === idMessage && m.statut === "streaming"
          ? { ...m, statut: "done" }
          : m
      )
    );
  }, []);

  return { messages, isLoading, sendMessage, marquerMessageTermine, sessionId };
}
