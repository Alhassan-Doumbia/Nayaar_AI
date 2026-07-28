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
 * `disabled` (ex. pendant qu'une réponse est en cours) bloque la saisie et
 * l'envoi, sans changer l'apparence par défaut du composant.
 *
 * @param {(texte: string) => void} [onSend]
 * @param {boolean} [disabled]
 */
export function ChatInput({ onSend, disabled = false }) {
  const [valeur, setValeur] = useState("");

  const envoyer = () => {
    if (!valeur.trim() || disabled) return;
    onSend?.(valeur.trim());
    setValeur("");
  };

  return (
    <PromptInput
      value={valeur}
      onValueChange={setValeur}
      onSubmit={envoyer}
      disabled={disabled}
      className="border-nayaar-gold-soft bg-white focus-within:ring-2 focus-within:ring-nayaar-gold/40"
    >
      <PromptInputTextarea placeholder="Décrivez ce que vous recherchez…" />
      <PromptInputActions className="justify-end pt-1">
        <PromptInputAction tooltip="Envoyer">
          <button
            type="button"
            onClick={envoyer}
            disabled={!valeur.trim() || disabled}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-nayaar-gold text-nayaar-cream transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        </PromptInputAction>
      </PromptInputActions>
    </PromptInput>
  );
}
