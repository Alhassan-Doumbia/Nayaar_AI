# -*- coding: utf-8 -*-
"""Route de consultation d'un parfum, lu depuis la Knowledge Base chargée en mémoire (aucune base de données)."""
from fastapi import APIRouter, HTTPException, Request

from routes.schemas import PerfumeDetail, ScoresMoment, ScoresSaison

router = APIRouter()


@router.get("/api/perfumes/{id}", response_model=PerfumeDetail)
def obtenir_parfum(id: int, request: Request):
    """
    Retourne la fiche complète d'un parfum. L'id est sa position dans la
    Knowledge Base au moment du chargement (même ordre que le CSV et que
    data/processed/nayaar_index_mapping.json — cohérent avec le reste du
    pipeline, pas un identifiant inventé pour l'API).
    """
    parfums = request.app.state.parfums

    if id < 0 or id >= len(parfums):
        raise HTTPException(status_code=404, detail=f"Aucun parfum avec l'id {id}.")

    parfum = parfums[id]

    return PerfumeDetail(
        id=id,
        nom=parfum["Name"],
        marque=parfum["Brand"],
        description=parfum["Description"],
        image_url=parfum.get("Image URL", ""),
        notes=parfum.get("notes_list", []),
        notes_categories=parfum.get("notes_categories", []),
        famille=parfum.get("famille", ""),
        profil=parfum.get("profil", ""),
        concentration=parfum.get("concentration", ""),
        scores_saison=ScoresSaison(
            winter=float(parfum["winter_score"]),
            spring=float(parfum["spring_score"]),
            summer=float(parfum["summer_score"]),
            autumn=float(parfum["autumn_score"]),
        ),
        scores_moment=ScoresMoment(
            day=float(parfum["day_score"]),
            night=float(parfum["night_score"]),
        ),
    )
