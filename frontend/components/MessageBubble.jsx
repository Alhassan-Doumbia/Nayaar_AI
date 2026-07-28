"use client";

import { motion } from "framer-motion";
import { Message, MessageContent } from "@/components/ui/message";

/**
 * Bulle de message, basée sur le composant Prompt Kit `Message` mais
 * re-stylée selon l'identité Nayaar :
 * - assistant : fond noir profond, texte crème, liseré doré sur le bord gauche
 * - utilisateur : fond beige clair, alignée à droite
 * Chaque bulle est précédée d'un label petites capitales ("ASSISTANT" / "VOUS").
 *
 * @param {"assistant"|"user"} role
 * @param {string} contenu - texte du message (rendu en markdown pour l'assistant)
 */
export function MessageBubble({ role, contenu }) {
  const estAssistant = role === "assistant";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className={`flex flex-col gap-1.5 ${estAssistant ? "items-start" : "items-end"}`}
    >
      <span className="label-caps px-1">
        {estAssistant ? "Assistant" : "Vous"}
      </span>

      <Message className={estAssistant ? "max-w-[75%]" : "max-w-[70%] flex-row-reverse"}>
        <MessageContent
          markdown={estAssistant}
          className={
            estAssistant
              ? // Bulle assistant : noir profond, texte crème, liseré doré à gauche
                "prose-invert rounded-2xl rounded-tl-sm border-l-2 border-nayaar-gold bg-nayaar-black px-4 py-3 text-sm leading-relaxed text-nayaar-cream"
              : // Bulle utilisateur : beige clair, alignée à droite
                "rounded-2xl rounded-tr-sm bg-nayaar-beige px-4 py-3 text-sm leading-relaxed text-nayaar-ink"
          }
        >
          {contenu}
        </MessageContent>
      </Message>
    </motion.div>
  );
}
