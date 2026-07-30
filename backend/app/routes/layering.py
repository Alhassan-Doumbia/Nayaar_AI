# -*- coding: utf-8 -*-
"""Route de layering : moteur de règles (layering.py) + Claude (layering_rag.py)."""
from fastapi import APIRouter, HTTPException

import layering_rag
from routes.schemas import LayeringRequest, LayeringResponse
from routes.utils import construire_parfum_layering, construire_reference_layering

router = APIRouter()


@router.post("/api/layering", response_model=LayeringResponse)
def proposer_layering(requete: LayeringRequest):
    """
    Pipeline complet : moteur de layering -> contexte -> Claude
    (layering_rag.py). Claude ne décide d'aucune compatibilité ; le rôle
    (base/dessus), le score et le classement viennent exclusivement du
    moteur de règles.

    Mode consultation autonome, comme /api/chat : pas d'historique, chaque
    appel est indépendant.
    """
    try:
        resultat = layering_rag.expliquer_layering(requete.perfume_id, n=requete.n)
    except IndexError as erreur:
        # perfume_id hors des limites de la Knowledge Base
        raise HTTPException(status_code=404, detail=str(erreur)) from erreur
    except RuntimeError as erreur:
        # ex. ANTHROPIC_API_KEY absente (voir backend/.env.example)
        raise HTTPException(status_code=500, detail=str(erreur)) from erreur

    return LayeringResponse(
        reply=resultat["reponse"],
        parfum_reference=construire_reference_layering(requete.perfume_id, resultat["parfum_reference"]),
        perfumes=[construire_parfum_layering(p) for p in resultat["propositions"]],
    )
