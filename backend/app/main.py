# -*- coding: utf-8 -*-
"""
API Nayaar — expose les moteurs backend (scoring, recherche sémantique
FAISS, moteur hybride, RAG Claude) au frontend Next.js, en local, sans base
de données externe : toutes les données vivent en fichiers
(nayaar_knowledge_base.csv, nayaar_index.faiss + son mapping,
notes_vocabulary.json), chargés une seule fois au démarrage (lifespan)
puis gardés en mémoire pour toutes les requêtes.

Lancer en local (accessible depuis cet ordinateur uniquement) :
    uvicorn main:app --reload --app-dir backend/app

Lancer en incluant l'accès depuis le réseau local (ex. téléphone sur le
même Wi-Fi, voir CORS_ORIGINS dans backend/.env) — --host 0.0.0.0 fait
écouter l'API sur toutes les interfaces réseau, pas seulement 127.0.0.1 :
    uvicorn main:app --reload --host 0.0.0.0 --app-dir backend/app
"""
import os
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Chemin explicite vers backend/.env, calculé depuis l'emplacement de ce
# fichier (__file__) — PAS load_dotenv(find_dotenv()), dont la détection
# automatique du dossier appelant (introspection de pile) est connue pour
# échouer silencieusement sous certains lanceurs (ex. le processus de
# rechargement d'`uvicorn --reload`), auquel cas .env n'est jamais chargé
# sans aucune erreur visible.
_DOSSIER_APP = os.path.dirname(os.path.abspath(__file__))
_CHEMIN_ENV = os.path.join(_DOSSIER_APP, "..", ".env")
load_dotenv(dotenv_path=_CHEMIN_ENV)

# Les modules métier (scoring, semantic_search, hybrid, rag) ne forment pas
# des packages Python formels dans ce projet (cohérence avec le style déjà
# utilisé partout ailleurs dans backend/app) : on ajoute leurs dossiers au
# chemin d'import avant de les importer, une seule fois, ici.
for _sous_dossier in ("recommendation", "chat"):
    sys.path.insert(0, os.path.join(_DOSSIER_APP, _sous_dossier))
sys.path.insert(0, _DOSSIER_APP)  # pour que "routes" soit importable comme package

import layering  # noqa: E402
import scoring  # noqa: E402
import semantic_search  # noqa: E402
from routes import chat, health, layering as layering_route, perfumes, recommend, search  # noqa: E402

RACINE_PROJET = os.path.abspath(os.path.join(_DOSSIER_APP, "..", ".."))


def _chemin_configurable(nom_variable_env, chemin_relatif_par_defaut):
    """Variable d'environnement si définie (backend/.env), sinon le chemin par défaut du projet."""
    valeur = os.environ.get(nom_variable_env)
    chemin = valeur if valeur else chemin_relatif_par_defaut
    return chemin if os.path.isabs(chemin) else os.path.join(RACINE_PROJET, chemin)


CHEMIN_KNOWLEDGE_BASE = _chemin_configurable(
    "NAYAAR_KNOWLEDGE_BASE_PATH", os.path.join("data", "processed", "nayaar_knowledge_base.csv")
)
CHEMIN_VOCABULAIRE = _chemin_configurable(
    "NAYAAR_VOCABULARY_PATH", os.path.join("data", "processed", "notes_vocabulary.json")
)

# Origines autorisées pour le CORS (frontend Next.js en local), séparées par des virgules dans .env
ORIGINES_CORS = [
    origine.strip()
    for origine in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origine.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Chargement unique au démarrage de l'API :
    - la Knowledge Base en mémoire (liste ordonnée : son index = l'id utilisé
      par GET /api/perfumes/{id}, le même ordre que l'index FAISS) ;
    - le mapping de normalisation des notes ;
    - le modèle d'embeddings et l'index FAISS (via le cache interne de
      semantic_search.py, réutilisé tel quel par le moteur hybride).
    Rien de tout ça n'est rechargé à chaque requête : les routes lisent ces
    ressources depuis request.app.state ou les caches de module déjà chauds.
    """
    app.state.parfums = scoring.charger_knowledge_base(CHEMIN_KNOWLEDGE_BASE)
    app.state.mapping_normalisation = scoring.charger_mapping_normalisation(CHEMIN_VOCABULAIRE)
    semantic_search._charger_ressources()  # charge le modèle + l'index FAISS une seule fois
    layering._charger_parfums()  # charge (une seule fois) la Knowledge Base propre au moteur de layering

    print(
        f"[Nayaar API] prêt : {len(app.state.parfums)} parfums, "
        f"{semantic_search._index.ntotal} vecteurs indexés."
    )
    yield
    # rien à libérer explicitement : pas de connexion externe ouverte (fichiers locaux uniquement)


app = FastAPI(
    title="Nayaar API",
    description="Moteurs de recommandation olfactive Nayaar (scoring par règles, recherche sémantique, RAG Claude).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINES_CORS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def gerer_erreur_inattendue(request: Request, exc: Exception):
    """
    Filet de sécurité : toute exception non gérée explicitement par une
    route renvoie une erreur 500 propre (JSON) plutôt qu'une trace Python
    brute exposée au client. Les erreurs attendues (clé API manquante,
    préférence invalide...) sont déjà gérées route par route avec un code
    et un message précis — ceci ne couvre que l'imprévu.
    """
    print(f"[Nayaar API] Erreur non gérée sur {request.url.path} : {exc!r}")
    return JSONResponse(status_code=500, content={"detail": "Erreur interne inattendue."})


app.include_router(health.router)
app.include_router(perfumes.router)
app.include_router(recommend.router)
app.include_router(chat.router)
app.include_router(layering_route.router)
app.include_router(search.router)
