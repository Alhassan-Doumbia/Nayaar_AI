# -*- coding: utf-8 -*-
"""
Pipeline RAG (Retrieval-Augmented Generation) de l'Assistant Nayaar.

Pipeline :
    question utilisateur
        -> moteur hybride (backend/app/recommendation/hybrid.py) : les
           5 meilleurs parfums, avec leur explication complète
        -> construction d'un contexte structuré (texte lisible par Claude)
        -> appel à Claude (API Anthropic) avec le system prompt strict de
           system_prompt.py
        -> réponse naturelle + données brutes du moteur

Conforme à CLAUDE.md : Claude ne décide jamais. Il ne reçoit que le
résultat déjà calculé par le moteur hybride et le reformule. S'il n'y a
aucun résultat pertinent, il le dit honnêtement (voir system_prompt.py,
règle 5) plutôt que d'inventer une recommandation.
"""
import os
import sys

from anthropic import Anthropic
from dotenv import load_dotenv, find_dotenv

from system_prompt import SYSTEM_PROMPT


# Charge automatiquement le fichier .env trouvé dans l'arborescence (si présent)
# afin que `os.environ` contienne les clés API définies par l'utilisateur.
load_dotenv(find_dotenv())

# Le moteur hybride vit dans backend/app/recommendation/, un dossier frère
# (pas un package Python formel dans ce projet — cohérent avec le style des
# autres modules backend). On l'ajoute explicitement au chemin d'import.
_DOSSIER_RECOMMENDATION = os.path.join(os.path.dirname(__file__), "..", "recommendation")
sys.path.insert(0, os.path.abspath(_DOSSIER_RECOMMENDATION))

import hybrid  # noqa: E402  (import après la manipulation de sys.path, nécessaire ici)


# ---------------------------------------------------------------------------
# Configuration — ajustable ici sans toucher au reste du code.
# ---------------------------------------------------------------------------
MODELE_CLAUDE = "claude-haiku-4-5-20251001"
NOMBRE_RESULTATS = 5

# En dessous de ce score hybride, un résultat est considéré comme non
# pertinent et retiré du contexte envoyé à Claude (plutôt que de forcer une
# recommandation faible juste parce que le pool n'était pas vide).
SEUIL_PERTINENCE_MINIMUM = 0.3


def _obtenir_client_anthropic():
    """
    Construit le client Anthropic à partir de la clé API lue dans la
    variable d'environnement ANTHROPIC_API_KEY — jamais en dur dans le code.
    Erreur explicite si elle est absente, plutôt qu'un échec réseau opaque.
    """
    cle_api = os.environ.get("ANTHROPIC_API_KEY")
    if not cle_api:
        raise RuntimeError(
            "La variable d'environnement ANTHROPIC_API_KEY n'est pas définie. "
            "Elle est nécessaire pour appeler l'API Claude."
        )
    return Anthropic(api_key=cle_api)


def construire_contexte(resultats):
    """
    Transforme les résultats du moteur hybride en un texte structuré et
    lisible, destiné à être injecté dans le message envoyé à Claude. Chaque
    parfum liste son score et le détail de chaque composante, pour que
    Claude puisse justifier sa recommandation sans rien inventer.

    Retourne un texte indiquant explicitement l'absence de résultat si la
    liste est vide, plutôt qu'un contexte vide ambigu.
    """
    if not resultats:
        return "Aucun résultat pertinent trouvé par le moteur de recommandation pour cette demande."

    blocs = []
    for rang, resultat in enumerate(resultats, start=1):
        contributions = resultat["details_regles"]
        bloc = (
            f"{rang}. {resultat['nom']} — {resultat['marque']}\n"
            f"   Famille olfactive : {resultat['famille']}\n"
            f"   Score global de correspondance : {resultat['score_hybride']} (sur 1.0)\n"
            f"   Contributions au score :\n"
            f"     - similarité de notes : {contributions['notes']}\n"
            f"     - correspondance de famille : {contributions['famille']}\n"
            f"     - correspondance de saison : {contributions['saison']}\n"
            f"     - correspondance de moment : {contributions['moment']}\n"
            f"     - correspondance de profil : {contributions['profil']}\n"
            f"     - proximité sémantique avec la demande : {resultat['score_semantique']}"
        )
        blocs.append(bloc)

    return "\n\n".join(blocs)


def _filtrer_resultats_pertinents(resultats, seuil=SEUIL_PERTINENCE_MINIMUM):
    """Retire les résultats dont le score hybride est trop faible pour être considérés pertinents."""
    return [r for r in resultats if r["score_hybride"] >= seuil]


def repondre(question_utilisateur, n_resultats=NOMBRE_RESULTATS, client=None):
    """
    Fonction principale du pipeline RAG.

    1. Appelle le moteur hybride pour obtenir les n_resultats meilleurs
       parfums (recherche sémantique + re-classement par règles).
    2. Filtre les résultats trop peu pertinents.
    3. Construit le contexte structuré.
    4. Envoie question + contexte à Claude, avec le system prompt strict.

    Retourne {"reponse": str, "resultats_bruts": list} : la reformulation
    naturelle de Claude, ET les données brutes du moteur (pour que le
    frontend puisse par exemple afficher le détail du score sans repasser
    par le LLM).
    """
    resultats_bruts = hybrid.recherche_hybride(question_utilisateur, n_resultats=n_resultats)
    resultats_pertinents = _filtrer_resultats_pertinents(resultats_bruts)

    contexte = construire_contexte(resultats_pertinents)

    if client is None:
        client = _obtenir_client_anthropic()

    message = client.messages.create(
        model=MODELE_CLAUDE,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Question du client : {question_utilisateur}\n\n"
                f"CONTEXTE (résultats du moteur de recommandation Nayaar, "
                f"du plus au moins pertinent) :\n\n{contexte}"
            ),
        }],
    )

    return {
        "reponse": message.content[0].text,
        "resultats_bruts": resultats_pertinents,
    }


if __name__ == "__main__":
    # question_exemple = "un parfum boisé et élégant pour un dîner d'hiver"
    question_exemple=input("Entrez votre question pour l'assistant Nayaar : ")
    resultat = repondre(question_exemple)

    print(f"Question : {question_exemple}\n")
    print("Réponse de l'assistant Nayaar :\n")
    print(resultat["reponse"])
    print("\n" + "=" * 80)
    print(f"\n{len(resultat['resultats_bruts'])} résultat(s) brut(s) utilisé(s) comme contexte.")
