"use client";

import { motion } from "framer-motion";
import { Message, MessageContent } from "@/components/ui/message";
import { Loader } from "@/components/ui/loader";
import { ResponseStream } from "@/components/ui/response-stream";
import { PerfumeCard } from "@/components/PerfumeCard";

// Réglage de la vitesse de révélation du texte (ResponseStream, mode
// typewriter). On fixe directement le nombre de caractères révélés par
// tick et le délai entre deux ticks, plutôt que de passer par le réglage
// `speed` générique du composant : à speed=35 (valeur par défaut utilisée
// auparavant), un seul caractère apparaissait toutes les ~17ms, soit
// ~8-10s pour une réponse de longueur normale — bien trop lent. Avec ces
// valeurs, ~4 caractères (environ un mot) apparaissent toutes les 18ms :
// une réponse de 500 caractères s'affiche entièrement en ~2,3s, tout en
// restant visiblement progressif (pas un "dump" brutal du texte entier).
const VITESSE_STREAM = {
  characterChunkSize: 4,
  segmentDelay: 18,
};

// Style de bulle partagé par tous les statuts assistant, pour ne pas le
// dupliquer entre les branches "loading" / "streaming" / "done" / "error".
const CLASSE_BULLE_ASSISTANT =
  "rounded-lg rounded-tl-sm border-l-2 border-nayaar-gold bg-nayaar-black px-4 py-3 font-sans text-[15px] leading-relaxed text-[#F5F0E8]";
const CLASSE_BULLE_UTILISATEUR =
  "rounded-lg rounded-tr-sm bg-nayaar-beige px-4 py-3 font-sans text-[15px] leading-relaxed text-nayaar-ink";

/**
 * Bulle de message, basée sur le composant Prompt Kit `Message`, re-stylée
 * selon l'identité Nayaar (assistant noir/liseré doré, utilisateur beige).
 *
 * Le contenu affiché dépend de `statut` :
 * - "loading"   : indicateur de frappe (Loader Prompt Kit)
 * - "streaming" : révélation progressive du texte (ResponseStream) ; le
 *                 texte complet est déjà connu (l'API ne fait pas de
 *                 streaming réseau token par token), c'est une animation
 *                 de lecture côté client
 * - "done"      : texte final, rendu markdown
 * - "error"     : message d'erreur, dans la même bulle assistant (élégant,
 *                 ne casse pas la mise en page), en italique pour le
 *                 distinguer d'une vraie réponse
 *
 * @param {"assistant"|"user"} role
 * @param {string} contenu
 * @param {"loading"|"streaming"|"done"|"error"} [statut]
 * @param {() => void} [onStreamComplete] - appelé quand l'animation de streaming se termine
 * @param {object} [parfumPrincipal] - si fourni (réponse "done" de l'assistant), la fiche
 *   parfum s'affiche À L'INTÉRIEUR de la bulle sombre, sous le texte (voir
 *   Docs/NAYAAR_DESIGN_DIRECTION.md section 5 — « c'est là que le luxe se voit le plus »)
 * @param {(perfumeId: number) => void} [onOpenLayering]
 */
export function MessageBubble({
  role,
  contenu,
  statut = "done",
  onStreamComplete,
  parfumPrincipal,
  onOpenLayering,
}) {
  const estAssistant = role === "assistant";
  const classeBulle = estAssistant ? CLASSE_BULLE_ASSISTANT : CLASSE_BULLE_UTILISATEUR;

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
        {statut === "loading" ? (
          <div className={`${classeBulle} flex items-center`}>
            <Loader variant="typing" size="sm" />
          </div>
        ) : statut === "streaming" ? (
          <div className={`${classeBulle} prose-nayaar-sombre`}>
            <ResponseStream
              textStream={contenu}
              mode="typewriter"
              characterChunkSize={VITESSE_STREAM.characterChunkSize}
              segmentDelay={VITESSE_STREAM.segmentDelay}
              onComplete={onStreamComplete}
            />
          </div>
        ) : statut === "error" ? (
          <div className={`${classeBulle} italic text-[#F5F0E8]/80`}>
            {contenu}
          </div>
        ) : (
          <div className={estAssistant && parfumPrincipal ? `${classeBulle} flex flex-col gap-4` : undefined}>
            <MessageContent
              markdown={estAssistant}
              className={
                estAssistant && parfumPrincipal
                  ? "bg-transparent p-0 prose-nayaar-sombre"
                  : `${classeBulle} ${estAssistant ? "prose-nayaar-sombre" : ""}`
              }
            >
              {contenu}
            </MessageContent>

            {estAssistant && parfumPrincipal && (
              <PerfumeCard
                parfum={parfumPrincipal}
                onOpenLayering={onOpenLayering}
                variante="sombre"
              />
            )}
          </div>
        )}
      </Message>
    </motion.div>
  );
}
