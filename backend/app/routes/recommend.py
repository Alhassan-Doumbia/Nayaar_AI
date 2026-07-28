# -*- coding: utf-8 -*-
"""Route de recommandation par préférences structurées — moteur de règles seul, jamais Claude."""
from fastapi import APIRouter, HTTPException, Request

import scoring
from routes.schemas import PreferencesRequest, RecommendResponse
from routes.utils import construire_lookup_parfums, construire_parfum_recommande

router = APIRouter()


@router.post("/api/recommend", response_model=RecommendResponse)
def recommander_par_preferences(preferences: PreferencesRequest, request: Request):
    """
    Applique directement le moteur de scoring (scoring.py) sur l'ensemble de
    la Knowledge Base, à partir de préférences déjà structurées — pas de
    texte libre, pas de recherche sémantique, pas d'appel à Claude. C'est le
    chemin "je sais exactement ce que je veux" de l'application.
    """
    parfums = request.app.state.parfums
    mapping_normalisation = request.app.state.mapping_normalisation

    preferences_dict = preferences.model_dump(exclude={"n"}, exclude_none=True)

    try:
        resultats = scoring.recommander(preferences_dict, parfums, mapping_normalisation, n=preferences.n)
    except ValueError as erreur:
        # ex. une famille/saison/moment/profil qui n'existe pas dans les valeurs connues de scoring.py
        raise HTTPException(status_code=400, detail=str(erreur)) from erreur

    lookup = construire_lookup_parfums(parfums)
    parfums_recommandes = [
        construire_parfum_recommande(resultat, lookup[(resultat["nom"], resultat["marque"])])
        for resultat in resultats
    ]

    return RecommendResponse(perfumes=parfums_recommandes)
