"use client";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ChatContainer } from "@/components/ChatContainer";
import { MessageBubble } from "@/components/MessageBubble";
import { PerfumeCard } from "@/components/PerfumeCard";
import { PerfumeGallery } from "@/components/PerfumeGallery";
import { SuggestionChips } from "@/components/SuggestionChips";
import { ChatInput } from "@/components/ChatInput";
import { CONVERSATION_EXEMPLE, SUGGESTIONS_EXEMPLE } from "@/lib/mock-data";

/**
 * Page de démonstration du chat Nayaar : assemble tous les composants avec
 * des données factices (CONVERSATION_EXEMPLE), sans aucun appel API ni
 * gestion d'état réelle — périmètre volontairement limité à la structure et
 * au style (le branchement à l'API FastAPI vient dans un prochain prompt).
 */
export default function Home() {
  return (
    <div className="flex h-screen flex-col bg-nayaar-cream">
      <Header />

      <main className="flex-1 overflow-hidden">
        <ChatContainer>
          {CONVERSATION_EXEMPLE.map((message) => (
            <div key={message.id} className="flex flex-col gap-4">
              <MessageBubble role={message.role} contenu={message.contenu} />

              {message.parfumPrincipal && (
                <PerfumeCard parfum={message.parfumPrincipal} />
              )}

              {message.galerie && <PerfumeGallery parfums={message.galerie} />}
            </div>
          ))}
        </ChatContainer>
      </main>

      <div className="mx-auto flex w-full max-w-2xl flex-col gap-3 px-4 pb-4">
        <SuggestionChips
          suggestions={SUGGESTIONS_EXEMPLE}
          onSelect={(id) => console.log("suggestion sélectionnée :", id)}
        />
        <ChatInput
          onSend={(texte) => console.log("message envoyé (factice) :", texte)}
        />
      </div>

      <Footer />
    </div>
  );
}
