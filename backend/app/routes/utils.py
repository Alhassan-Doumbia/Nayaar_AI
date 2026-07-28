# -*- coding: utf-8 -*-
"""
Fonctions partagées entre les routes de l'API Nayaar : transformation des
résultats des moteurs (scoring.py / hybrid.py) vers les schémas Pydantic
exposés par l'API. Centralisé ici pour ne pas dupliquer cette logique entre
routes/chat.py et routes/recommend.py, qui affichent toutes les deux des
parfums scorés.
"""
from routes.schemas import ContributionsScore, ParfumRecommande

# Nombre de notes affichées comme "notes principales" d'un parfum. notes_list
# n'a pas de hiérarchie tête/cœur/fond (voir notebook 02) : on affiche
# simplement les N premières notes listées, pas les "plus importantes".
NB_NOTES_PRINCIPALES = 5


def construire_lookup_parfums(parfums):
    """Construit un dict (nom, marque) -> parfum complet, pour retrouver les infos manquantes d'un résultat de moteur."""
    return {(p["Name"], p["Brand"]): p for p in parfums}


def construire_parfum_recommande(resultat_moteur, parfum_complet):
    """
    Assemble un ParfumRecommande à partir :
    - d'un résultat de moteur, qui peut venir de scoring.recommander()
      (clés "score_final"/"details") ou de hybrid.recherche_hybride()
      (clés "score_hybride"/"details_regles") — les deux formats sont gérés
      ici pour que /api/recommend et /api/chat réutilisent la même fonction ;
    - du parfum complet (Knowledge Base), pour l'image et les notes, que le
      résultat de moteur ne contient pas.
    """
    score = resultat_moteur.get("score_hybride", resultat_moteur.get("score_final"))
    details = resultat_moteur.get("details_regles", resultat_moteur.get("details"))

    return ParfumRecommande(
        nom=resultat_moteur["nom"],
        marque=resultat_moteur["marque"],
        image_url=parfum_complet.get("Image URL", ""),
        notes_principales=parfum_complet.get("notes_list", [])[:NB_NOTES_PRINCIPALES],
        famille=parfum_complet.get("famille", ""),
        score_compatibilite=score,
        details=ContributionsScore(**details),
    )
