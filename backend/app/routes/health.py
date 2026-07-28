# -*- coding: utf-8 -*-
"""Route de supervision : vérifie que tout ce qui doit être chargé en mémoire l'est vraiment."""
from fastapi import APIRouter, Request

import semantic_search
from routes.schemas import HealthResponse

router = APIRouter()


@router.get("/api/health", response_model=HealthResponse)
def verifier_sante(request: Request):
    """
    Vérifie l'état des trois ressources coûteuses chargées au démarrage
    (lifespan de main.py) : la Knowledge Base en mémoire, l'index FAISS et
    le modèle d'embeddings. Utile pour un check de déploiement local ou un
    healthcheck de conteneur, sans jamais recharger quoi que ce soit ici.
    """
    parfums = getattr(request.app.state, "parfums", [])

    # semantic_search gère son propre cache interne (chargé par le lifespan
    # via semantic_search._charger_ressources()) ; on le lit ici en lecture
    # seule pour vérifier son état, sans jamais le recharger.
    index_charge = semantic_search._index is not None
    modele_charge = semantic_search._modele is not None
    nb_vecteurs = semantic_search._index.ntotal if index_charge else 0

    knowledge_base_chargee = len(parfums) > 0
    statut = "ok" if (knowledge_base_chargee and index_charge and modele_charge) else "degrade"

    return HealthResponse(
        statut=statut,
        knowledge_base_chargee=knowledge_base_chargee,
        nb_parfums=len(parfums),
        index_faiss_charge=index_charge,
        nb_vecteurs_index=nb_vecteurs,
        modele_embeddings_charge=modele_charge,
    )
