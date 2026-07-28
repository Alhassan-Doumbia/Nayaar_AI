"use client";

import { motion } from "framer-motion";
import { PromptSuggestion } from "@/components/ui/prompt-suggestion";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

/**
 * Chips de suggestion rapide, basées sur `PromptSuggestion` de Prompt Kit.
 * Le chip "Suggérer un layering" est désactivé (grisé + infobulle) car le
 * Layering Engine est hors MVP (voir Docs/MVP_SCOPE.md).
 *
 * @param {object[]} suggestions - { id, label, disabled, tooltip }
 * @param {(id: string) => void} [onSelect] - callback de sélection (câblé au prompt suivant)
 */
export function SuggestionChips({ suggestions, onSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((suggestion) => {
        const chip = (
          <motion.div
            key={suggestion.id}
            whileHover={suggestion.disabled ? undefined : { y: -2 }}
            transition={{ duration: 0.15 }}
          >
            <PromptSuggestion
              onClick={() => !suggestion.disabled && onSelect?.(suggestion.id)}
              className={
                suggestion.disabled
                  ? "cursor-not-allowed border-nayaar-gold-soft/40 text-nayaar-label opacity-60"
                  : "border-nayaar-gold-soft text-nayaar-ink hover:border-nayaar-gold hover:bg-nayaar-cream-deep"
              }
              // On garde le bouton cliquable au sens accessible (pas l'attribut
              // HTML "disabled") pour que le survol continue de déclencher le
              // tooltip ; c'est le clic lui-même qui est neutralisé au-dessus.
              aria-disabled={suggestion.disabled}
            >
              {suggestion.label}
            </PromptSuggestion>
          </motion.div>
        );

        if (!suggestion.disabled) return chip;

        // Base UI (pas Radix) : pas de prop `asChild`, on compose via `render`
        // pour que le Trigger s'affiche comme notre chip plutôt que comme un
        // <button> par défaut (voir node_modules/@base-ui/react/docs/.../composition.md).
        return (
          <Tooltip key={suggestion.id}>
            <TooltipTrigger render={<span className="inline-flex">{chip}</span>} />
            <TooltipContent>{suggestion.tooltip}</TooltipContent>
          </Tooltip>
        );
      })}
    </div>
  );
}
