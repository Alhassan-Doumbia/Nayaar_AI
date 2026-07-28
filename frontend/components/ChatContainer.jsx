"use client";

import {
  ChatContainerRoot,
  ChatContainerContent,
  ChatContainerScrollAnchor,
} from "@/components/ui/chat-container";
import { ScrollButton } from "@/components/ui/scroll-button";

/**
 * Zone de conversation défilante, basée sur `chat-container` de Prompt Kit
 * (auto-scroll vers le bas géré par `use-stick-to-bottom`, cf. mécanique
 * conservée telle quelle). Affiche un bouton "revenir en bas" quand
 * l'utilisateur remonte dans l'historique.
 */
export function ChatContainer({ children }) {
  return (
    <ChatContainerRoot className="relative h-full w-full">
      <ChatContainerContent className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-4 py-8">
        {children}
        <ChatContainerScrollAnchor />
      </ChatContainerContent>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2">
        <ScrollButton className="border-nayaar-gold-soft bg-white text-nayaar-gold shadow-md hover:bg-nayaar-cream-deep" />
      </div>
    </ChatContainerRoot>
  );
}
