"use client";

import { useState } from "react";
import { ArrowUp } from "lucide-react";
import {
  PromptInput,
  PromptInputTextarea,
  PromptInputActions,
  PromptInputAction,
} from "@/components/ui/prompt-input";

/**
 * Champ de saisie du chat, basé sur `PromptInput` de Prompt Kit (auto-resize,
 * envoi sur Entrée), re-stylé avec le bouton d'envoi rond doré de Nayaar.
 *
 * Pas de gestion d'état/API à ce stade (périmètre de ce prompt) : onSend
 * n'est appelé qu'avec le texte saisi, câblage réel au prompt suivant.
 *
 * @param {(texte: string) => void} [onSend]
 */
export function ChatInput({ onSend }) {
  const [valeur, setValeur] = useState("");

  const envoyer = () => {
    if (!valeur.trim()) return;
    onSend?.(valeur.trim());
    setValeur("");
  };

  return (
    <PromptInput
      value={valeur}
      onValueChange={setValeur}
      onSubmit={envoyer}
      className="border-nayaar-gold-soft bg-white focus-within:ring-2 focus-within:ring-nayaar-gold/40"
    >
      <PromptInputTextarea placeholder="Décrivez ce que vous recherchez…" />
      <PromptInputActions className="justify-end pt-1">
        <PromptInputAction tooltip="Envoyer">
          <button
            type="button"
            onClick={envoyer}
            disabled={!valeur.trim()}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-nayaar-gold text-nayaar-cream transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </PromptInputAction>
      </PromptInputActions>
    </PromptInput>
  );
}
