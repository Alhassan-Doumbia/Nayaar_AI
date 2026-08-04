"use client";

import { useState } from "react";
import Link from "next/link";
import { Layers } from "lucide-react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatContainer } from "@/components/ChatContainer";
import { MessageBubble } from "@/components/MessageBubble";
import { PerfumeCard } from "@/components/PerfumeCard";
import { PerfumeGallery } from "@/components/PerfumeGallery";
import { SuggestionChips } from "@/components/SuggestionChips";
import { ChatInput } from "@/components/ChatInput";
import { LayeringPanel } from "@/components/LayeringPanel";
import { useChat } from "@/hooks/useChat";

// Chips de suggestion rapide. Mode consultation autonome : chaque chip
// déclenche une NOUVELLE recherche indépendante (texte pré-rempli, sans
// référence à l'échange précédent) — jamais un suivi de la réponse
// précédente. "Pourquoi ce choix ?" a disparu : le backend inclut
// désormais systématiquement l'explication dans sa première réponse (voir
// backend/app/chat/system_prompt.py). Le chip "Suggérer un layering" a
// disparu lui aussi : le layering est maintenant actif, mais contextuel à
// UN parfum précis (bouton dédié sur PerfumeCard), pas une action globale
// du fil de discussion.
const SUGGESTIONS = [
  {
    id: "fraicheur",
    label: "Une alternative plus fraîche",
    texte: "Un parfum frais et léger",
    disabled: false,
  },
];

export default function Home() {
  const { messages, isLoading, sendMessage, marquerMessageTermine } = useChat();

  // Id du parfum pour lequel le panneau de layering est ouvert (null =
  // fermé). État local à la page, complètement indépendant de useChat :
  // ouvrir/fermer le panneau ne touche jamais au fil de conversation.
  const [layeringPerfumeId, setLayeringPerfumeId] = useState(null);

  const suggestionsAffichees = SUGGESTIONS.map((s) => ({
    ...s,
    disabled: s.disabled || isLoading,
  }));

  const selectionnerSuggestion = (id) => {
    const suggestion = SUGGESTIONS.find((s) => s.id === id);
    if (suggestion?.texte) sendMessage(suggestion.texte);
  };

  return (
    <div className="flex h-screen flex-col bg-nayaar-cream">
      <Header
        nav={
          <Link
            href="/layering"
            className="label-caps flex items-center gap-1.5 text-nayaar-ink/70 transition-colors hover:text-nayaar-gold"
          >
            <Layers className="h-3.5 w-3.5" />
            Layering
          </Link>
        }
      />

      <main className="flex-1 overflow-hidden">
        <ChatContainer>
          {messages.length === 0 && (
            <p className="mx-auto mt-12 max-w-sm text-center font-serif text-lg text-nayaar-ink/60">
              Décrivez le parfum que vous recherchez, l&apos;occasion, ou
              l&apos;émotion que vous souhaitez porter.
            </p>
          )}

          {messages.map((message) => (
            <div key={message.id} className="flex flex-col gap-4">
              <MessageBubble
                role={message.role}
                contenu={message.contenu}
                statut={message.statut}
                onStreamComplete={() => marquerMessageTermine(message.id)}
              />

              {/* Le premier parfum se démarque toujours en grande carte
                  détaillée ; s'il y en a d'autres, ils suivent en petites
                  vignettes défilantes (alternatives), jamais l'inverse. */}
              {message.perfumes?.length > 0 && (
                <PerfumeCard
                  parfum={message.perfumes[0]}
                  onOpenLayering={setLayeringPerfumeId}
                />
              )}

              {message.perfumes?.length > 1 && (
                <PerfumeGallery parfums={message.perfumes.slice(1)} />
              )}
            </div>
          ))}
        </ChatContainer>
      </main>

      <div className="mx-auto flex w-full max-w-2xl flex-col gap-3 px-4 pb-4">
        <SuggestionChips
          suggestions={suggestionsAffichees}
          onSelect={selectionnerSuggestion}
        />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>

      <Footer />

      {/* Couche par-dessus tout le reste ; ne modifie jamais l'état du chat derrière. */}
      <LayeringPanel
        perfumeId={layeringPerfumeId}
        onClose={() => setLayeringPerfumeId(null)}
      />
    </div>
  );
}
