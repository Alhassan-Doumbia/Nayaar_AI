# -*- coding: utf-8 -*-
"""
Modèles Pydantic partagés entre les routes de l'API Nayaar.

Centralisés ici pour éviter de redéfinir deux fois le même schéma (ex.
ParfumRecommande est utilisé par /api/chat ET /api/recommend, qui
retournent tous les deux des parfums scorés avec leur explication).
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ContributionsScore(BaseModel):
    """Détail des composantes du score de règles (scoring.py), toutes déjà pondérées."""
    notes: float
    famille: float
    saison: float
    moment: float
    profil: float


class ParfumRecommande(BaseModel):
    """Un parfum recommandé, avec assez d'information pour l'afficher et l'expliquer côté frontend."""
    nom: str
    marque: str
    image_url: str
    notes_principales: list[str]
    famille: str
    score_compatibilite: float = Field(..., description="Score final (règles seules pour /api/recommend, hybride pour /api/chat), entre 0 et 1.")
    details: ContributionsScore


# --- /api/chat -----------------------------------------------------------
# Mode consultation autonome : chaque appel est indépendant, pas
# d'historique dans la requête (voir backend/app/chat/rag.py).
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Question ou demande du client, en langage naturel.")
    session_id: Optional[str] = Field(None, description="Identifiant de session côté client ; généré si absent, non utilisé pour la génération de la réponse.")


class ChatResponse(BaseModel):
    reply: str
    perfumes: list[ParfumRecommande]
    session_id: str


# --- /api/recommend --------------------------------------------------------
class PreferencesRequest(BaseModel):
    """Préférences structurées — pas de texte libre, pas de passage par Claude."""
    notes_aimees: list[str] = Field(default_factory=list)
    famille_preferee: Optional[str] = None
    saison: Optional[str] = None
    moment: Optional[str] = None
    profil: Optional[str] = None
    marques_exclues: list[str] = Field(default_factory=list)
    n: int = Field(5, ge=1, le=50, description="Nombre de recommandations souhaitées.")


class RecommendResponse(BaseModel):
    perfumes: list[ParfumRecommande]


# --- /api/perfumes/{id} -----------------------------------------------------
class ScoresSaison(BaseModel):
    winter: float
    spring: float
    summer: float
    autumn: float


class ScoresMoment(BaseModel):
    day: float
    night: float


class PerfumeDetail(BaseModel):
    """Fiche complète d'un parfum, lue depuis la Knowledge Base chargée en mémoire."""
    id: int
    nom: str
    marque: str
    description: str
    image_url: str
    notes: list[str]
    notes_categories: list[str]
    famille: str
    profil: str
    concentration: str
    scores_saison: ScoresSaison
    scores_moment: ScoresMoment


# --- /api/health -------------------------------------------------------------
class HealthResponse(BaseModel):
    statut: Literal["ok", "degrade"]
    knowledge_base_chargee: bool
    nb_parfums: int
    index_faiss_charge: bool
    nb_vecteurs_index: int
    modele_embeddings_charge: bool
