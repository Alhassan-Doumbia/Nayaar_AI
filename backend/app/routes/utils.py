# -*- coding: utf-8 -*-
"""
Fonctions partagées entre les routes de l'API Nayaar : transformation des
résultats des moteurs (scoring.py / hybrid.py) vers les schémas Pydantic
exposés par l'API. Centralisé ici pour ne pas dupliquer cette logique entre
routes/chat.py et routes/recommend.py, qui affichent toutes les deux des
parfums scorés.
"""
from routes.schemas import (
    ContributionsLayering,
    ContributionsScore,
    ParfumLayering,
    ParfumRecommande,
    ParfumReferenceLayering,
)

# Nombre de notes affichées comme "notes principales" d'un parfum. notes_list
# n'a pas de hiérarchie tête/cœur/fond (voir notebook 02) : on affiche
# simplement les N premières notes listées, pas les "plus importantes".
NB_NOTES_PRINCIPALES = 5


def construire_lookup_parfums(parfums):
    """
    Construit un dict (nom, marque) -> (id, parfum complet). id = position
    dans la Knowledge Base (même convention que GET /api/perfumes/{id} et
    POST /api/layering) : nécessaire pour que le frontend puisse ouvrir le
    panneau de layering sur un parfum recommandé par /api/chat ou /api/recommend.
    """
    return {(p["Name"], p["Brand"]): (position, p) for position, p in enumerate(parfums)}


def construire_parfum_recommande(resultat_moteur, perfume_id, parfum_complet):
    """
    Assemble un ParfumRecommande à partir :
    - d'un résultat de moteur, qui peut venir de scoring.recommander()
      (clés "score_final"/"details") ou de hybrid.recherche_hybride()
      (clés "score_hybride"/"details_regles") — les deux formats sont gérés
      ici pour que /api/recommend et /api/chat réutilisent la même fonction ;
    - de l'id (position dans la Knowledge Base) et du parfum complet, issus
      de construire_lookup_parfums, pour l'image/les notes/l'id que le
      résultat de moteur ne contient pas.
    """
    score = resultat_moteur.get("score_hybride", resultat_moteur.get("score_final"))
    details = resultat_moteur.get("details_regles", resultat_moteur.get("details"))

    return ParfumRecommande(
        id=perfume_id,
        nom=resultat_moteur["nom"],
        marque=resultat_moteur["marque"],
        image_url=parfum_complet.get("Image URL", ""),
        notes_principales=parfum_complet.get("notes_list", [])[:NB_NOTES_PRINCIPALES],
        famille=parfum_complet.get("famille", ""),
        score_compatibilite=score,
        details=ContributionsScore(**details),
    )


def construire_parfum_layering(proposition):
    """Assemble un ParfumLayering à partir d'une proposition brute de layering.proposer_layering()."""
    return ParfumLayering(
        nom=proposition["nom"],
        marque=proposition["marque"],
        image_url=proposition["image_url"],
        score_compatibilite=proposition["score_compatibilite"],
        details=ContributionsLayering(**proposition["details"]),
        role=proposition["role"],
    )


def construire_reference_layering(perfume_id, parfum_complet):
    """Assemble un ParfumReferenceLayering (parfum de départ) pour l'affichage côté panneau de layering."""
    return ParfumReferenceLayering(
        id=perfume_id,
        nom=parfum_complet["Name"],
        marque=parfum_complet["Brand"],
        image_url=parfum_complet.get("Image URL", ""),
        famille=parfum_complet.get("famille", ""),
        notes_principales=parfum_complet.get("notes_list", [])[:NB_NOTES_PRINCIPALES],
    )
