# -*- coding: utf-8 -*-
"""
Pipeline RAG du guide de superposition (layering) de l'Assistant Nayaar.

Pipeline :
    perfume_id, n
        -> moteur de layering (backend/app/recommendation/layering.py) :
           les n parfums les plus compatibles, avec score, détail des
           contributions et rôle suggéré (base/dessus)
        -> construction d'un contexte structuré (texte lisible par Claude)
        -> appel à Claude (API Anthropic) avec le system prompt dédié de
           layering_system_prompt.py
        -> guide de superposition rédigé + données brutes du moteur

Mode de fonctionnement : consultation autonome, un tour unique — comme
rag.py (voir ce fichier pour le détail du raisonnement). Aucun historique
n'est conservé ni transmis à Claude.

Conforme à CLAUDE.md : Claude ne décide jamais des compatibilités, elles
viennent exclusivement du moteur de règles. Il reformule et met en forme.
"""
import os
import sys

from dotenv import load_dotenv

from layering_system_prompt import LAYERING_SYSTEM_PROMPT

# Chemin explicite vers backend/.env (voir main.py pour le détail : PAS
# load_dotenv(find_dotenv()), dont la détection automatique échoue
# silencieusement sous certains lanceurs).
_CHEMIN_ENV = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_CHEMIN_ENV)

# layering.py vit dans backend/app/recommendation/, un dossier frère (pas
# un package Python formel dans ce projet — cohérent avec le style des
# autres modules backend, voir rag.py).
_DOSSIER_RECOMMENDATION = os.path.join(os.path.dirname(__file__), "..", "recommendation")
sys.path.insert(0, os.path.abspath(_DOSSIER_RECOMMENDATION))

import layering  # noqa: E402  (import après la manipulation de sys.path, nécessaire ici)

# Le client Anthropic et le modèle utilisé sont déjà définis dans rag.py
# (pipeline du chat principal) : on les réutilise tels quels plutôt que de
# dupliquer cette configuration, pour ne jamais avoir deux modèles ou deux
# façons de construire le client qui divergent silencieusement.
from rag import MODELE_CLAUDE, _obtenir_client_anthropic  # noqa: E402

NOMBRE_PROPOSITIONS_PAR_DEFAUT = 3


def construire_contexte_layering(parfum_reference, propositions):
    """
    Transforme le parfum de référence et les propositions du moteur en un
    texte structuré et lisible pour Claude. Chaque proposition liste son
    rôle et le détail de ses contributions, pour que Claude puisse
    justifier l'association et l'ordre d'application sans rien inventer.
    """
    bloc_reference = (
        f"PARFUM DE RÉFÉRENCE : {parfum_reference['Name']} — {parfum_reference['Brand']}\n"
        f"Famille olfactive : {parfum_reference.get('famille') or 'non déterminée'}"
    )

    if not propositions:
        return (
            f"{bloc_reference}\n\n"
            "Aucune proposition de layering pertinente n'a été trouvée par le moteur."
        )

    blocs_propositions = []
    for rang, proposition in enumerate(propositions, start=1):
        contributions = proposition["details"]
        bloc = (
            f"{rang}. {proposition['nom']} — {proposition['marque']}\n"
            f"   Rôle suggéré : {proposition['role']} "
            f"({'à appliquer en dessous, porte la tenue' if proposition['role'] == 'base' else 'à appliquer par-dessus, plus frais/volatil'})\n"
            f"   Score de compatibilité : {proposition['score_compatibilite']} (sur 1.0)\n"
            f"   Contributions au score :\n"
            f"     - accord de familles olfactives : {contributions['categories']}\n"
            f"     - complémentarité (nouveauté apportée) : {contributions['complementarite']}\n"
            f"     - cohérence saison / moment : {contributions['saison_moment']}\n"
            f"     - cohérence de profil : {contributions['profil']}"
        )
        blocs_propositions.append(bloc)

    return bloc_reference + "\n\n" + "\n\n".join(blocs_propositions)


def expliquer_layering(perfume_id, n=NOMBRE_PROPOSITIONS_PAR_DEFAUT, client=None):
    """
    Fonction principale du pipeline RAG de layering.

    1. Appelle le moteur de layering pour obtenir les n parfums les plus
       compatibles avec le parfum de référence (perfume_id), avec leur
       rôle suggéré (base/dessus).
    2. Construit le contexte structuré.
    3. Envoie le contexte à Claude, avec le system prompt dédié, qui
       rédige un guide de superposition complet en une seule réponse.

    Retourne {"reponse": str, "parfum_reference": dict, "propositions": list} :
    la reformulation de Claude, ET les données brutes du moteur (parfum de
    référence complet + propositions), pour que l'API puisse construire les
    cartes du panneau sans repasser par le LLM.

    Lève IndexError si perfume_id est hors limites (propagé tel quel depuis
    layering.proposer_layering, à charge de l'appelant — la route API — de
    le traduire en réponse HTTP appropriée).
    """
    parfums = layering._charger_parfums()

    # proposer_layering valide perfume_id et lève un IndexError explicite
    # ("Aucun parfum avec l'id ...") si besoin — on l'appelle AVANT d'indexer
    # nous-mêmes parfums[perfume_id], pour ne jamais laisser échapper le
    # IndexError générique de Python ("list index out of range") côté API.
    propositions = layering.proposer_layering(perfume_id, n=n, parfums=parfums)
    parfum_reference = parfums[perfume_id]

    contexte = construire_contexte_layering(parfum_reference, propositions)

    if client is None:
        client = _obtenir_client_anthropic()

    message = client.messages.create(
        model=MODELE_CLAUDE,
        max_tokens=1024,
        system=LAYERING_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Compose un guide de superposition à partir du CONTEXTE suivant "
                f"(résultats du moteur de layering Nayaar) :\n\n{contexte}"
            ),
        }],
    )

    return {
        "reponse": message.content[0].text,
        "parfum_reference": parfum_reference,
        "propositions": propositions,
    }


if __name__ == "__main__":
    id_exemple = int(input("Entrez l'id du parfum de référence : "))

    resultat = expliquer_layering(id_exemple)

    print(f"\nParfum de référence : {resultat['parfum_reference']['Name']} — {resultat['parfum_reference']['Brand']}\n")
    print("Guide de superposition :\n")
    print(resultat["reponse"])
    print("\n" + "=" * 80)
    print(f"\n{len(resultat['propositions'])} proposition(s) brute(s) utilisée(s) comme contexte.")
