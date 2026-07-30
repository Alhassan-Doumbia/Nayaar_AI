# -*- coding: utf-8 -*-
"""Route de recherche textuelle par nom/marque — pour l'autocomplétion (pas de recherche sémantique)."""
from fastapi import APIRouter, Query, Request

import search_by_name
from routes.schemas import ResultatRecherche

router = APIRouter()


@router.get("/api/search", response_model=list[ResultatRecherche])
def rechercher(request: Request, q: str = Query("", description="Texte tapé par le client (nom ou marque de parfum).")):
    """
    Recherche textuelle simple sur la Knowledge Base déjà chargée en
    mémoire (request.app.state.parfums, chargée une seule fois au
    démarrage de l'API — voir main.py). Aucun rechargement ici.

    Retourne toujours une liste (vide si q est vide ou si rien ne
    correspond) : pas d'erreur 404/400 pour une recherche sans résultat,
    c'est un cas normal d'autocomplétion.
    """
    return search_by_name.rechercher_par_nom(q, request.app.state.parfums)
