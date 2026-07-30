import { LayeringPerfumeCard } from "@/components/LayeringPerfumeCard";
import { Markdown } from "@/components/ui/markdown";

/**
 * Mise en page des résultats d'un layering : cartes des parfums proposés
 * (avec badge de rôle base/dessus, score animé, bouton copier) puis le
 * guide rédigé par Claude. Extrait de LayeringPanel (volet latéral) pour
 * être réutilisé tel quel sur la page /layering (résultats en pleine page).
 *
 * @param {object[]} perfumes - propositions du moteur (voir LayeringPerfumeCard)
 * @param {string} reply - guide de superposition rédigé par Claude (markdown)
 */
export function LayeringResults({ perfumes, reply }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-3">
        {perfumes.map((parfum) => (
          <LayeringPerfumeCard
            key={`${parfum.nom}-${parfum.marque}`}
            parfum={parfum}
          />
        ))}
      </div>

      <Markdown className="prose prose-sm max-w-none text-nayaar-ink prose-headings:font-serif prose-headings:text-nayaar-ink prose-strong:text-nayaar-ink">
        {reply}
      </Markdown>
    </div>
  );
}
