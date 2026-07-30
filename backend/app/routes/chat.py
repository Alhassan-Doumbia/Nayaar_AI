# -*- coding: utf-8 -*-
"""Route conversationnelle : moteur hybride + Claude (RAG), voir backend/app/chat/rag.py."""
import uuid

from fastapi import APIRouter, HTTPException, Request

import rag
from routes.schemas import ChatRequest, ChatResponse
from routes.utils import construire_lookup_parfums, construire_parfum_recommande

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
def discuter(requete: ChatRequest, request: Request):
    """
    Pipeline complet : recherche hybride -> contexte -> Claude (rag.py).
    Claude ne fait que reformuler ; les parfums retournés viennent
    exclusivement du moteur, jamais du texte généré par Claude.

    Mode consultation autonome : chaque appel est traité indépendamment,
    sans historique (voir rag.py). session_id est uniquement renvoyé tel
    quel pour que le frontend puisse regrouper des échanges côté affichage
    si besoin ; il n'influence pas la réponse générée.
    """
    session_id = requete.session_id or str(uuid.uuid4())

    try:
        resultat = rag.repondre(requete.message)
    except RuntimeError as erreur:
        # ex. ANTHROPIC_API_KEY absente (voir backend/.env.example)
        raise HTTPException(status_code=500, detail=str(erreur)) from erreur
    except KeyError as erreur:
        # ex. désynchronisation entre l'index FAISS et la Knowledge Base
        raise HTTPException(status_code=500, detail=str(erreur)) from erreur

    lookup = construire_lookup_parfums(request.app.state.parfums)
    parfums_recommandes = [
        construire_parfum_recommande(r, *lookup[(r["nom"], r["marque"])])
        for r in resultat["resultats_bruts"]
        if (r["nom"], r["marque"]) in lookup
    ]

    return ChatResponse(reply=resultat["reponse"], perfumes=parfums_recommandes, session_id=session_id)
