# -*- coding: utf-8 -*-
"""
Moteur de scoring Nayaar.

Prend en entrée des préférences utilisateur et une liste de parfums (issus de
la Nayaar Knowledge Base, data/processed/nayaar_knowledge_base.csv), et
retourne les N parfums les mieux notés, avec le détail de chaque composante
du score.

Philosophie du projet (voir CLAUDE.md) : GPT/l'IA ne décide jamais seul d'une
recommandation. Ce module ne contient donc AUCUN appel à un LLM — uniquement
des règles de scoring explicites, pures et testables.
"""
import csv
import json
import os


# ---------------------------------------------------------------------------
# Configuration des poids — ajustable ici sans toucher au reste du code.
# La somme doit rester égale à 1.0 (vérifié au chargement du module).
# ---------------------------------------------------------------------------
POIDS_SCORING = {
    "notes": 0.35,
    "famille": 0.25,
    "saison": 0.20,
    "moment": 0.10,
    "profil": 0.10,
}

assert abs(sum(POIDS_SCORING.values()) - 1.0) < 1e-9, "La somme des poids doit être égale à 1.0"

# Les 12 familles olfactives connues (mêmes valeurs que CATEGORIES dans le
# notebook 03a). Sert à valider famille_preferee plutôt que de laisser une
# faute de frappe passer inaperçue.
FAMILLES_CONNUES = {
    "agrumes", "floral", "boise", "epice", "oriental_ambre", "aromatique",
    "fruite", "gourmand", "musque", "vert", "aquatique", "cuir",
}

# Traductions acceptées en entrée -> clé interne utilisée dans les colonnes
# de la Knowledge Base (winter_score, day_score, profil...).
TRADUCTION_SAISON = {
    "winter": "winter", "hiver": "winter",
    "spring": "spring", "printemps": "spring",
    "summer": "summer", "ete": "summer", "été": "summer",
    "autumn": "autumn", "automne": "autumn",
}
TRADUCTION_MOMENT = {
    "day": "day", "jour": "day",
    "night": "night", "nuit": "night",
}
TRADUCTION_PROFIL = {
    "masculine": "masculine", "masculin": "masculine",
    "feminine": "feminine", "féminin": "feminine", "feminin": "feminine",
    "unisex": "unisex", "unisexe": "unisex",
}


def _traduire(valeur, table_traduction, nom_champ):
    """
    Traduit une valeur de préférence (FR ou EN, insensible à la casse) vers
    la clé interne utilisée par la Knowledge Base.
    """
    traduction = table_traduction.get(str(valeur).strip().lower())
    if traduction is None:
        raise ValueError(
            f"Valeur inconnue pour {nom_champ!r} : {valeur!r}. "
            f"Valeurs acceptées : {sorted(set(table_traduction))}"
        )
    return traduction


# Compatibilité entre le profil demandé et le profil du parfum.
COMPATIBILITE_PROFIL = {
    ("masculine", "masculine"): 1.0,
    ("masculine", "unisex"): 0.5,
    ("masculine", "feminine"): 0.0,
    ("feminine", "feminine"): 1.0,
    ("feminine", "unisex"): 0.5,
    ("feminine", "masculine"): 0.0,
    ("unisex", "unisex"): 1.0,
    ("unisex", "masculine"): 0.0,
    ("unisex", "feminine"): 0.0,
}


# ---------------------------------------------------------------------------
# Fonctions de scoring par composante — chacune pure, testable isolément.
# ---------------------------------------------------------------------------
def normaliser_notes(notes_brutes, mapping_normalisation):
    """
    Normalise une liste de notes brutes en un ensemble de notes canoniques.
    """
    resultat = set()
    for note in notes_brutes:
        note_minuscule = str(note).strip().lower()
        resultat.add(mapping_normalisation.get(note_minuscule, note_minuscule))
    return resultat


def score_similarite_notes(notes_aimees, notes_parfum, mapping_normalisation):
    """
    Taux de rappel (recall) des notes aimées par l'utilisateur.
    """
    ensemble_aimees = normaliser_notes(notes_aimees, mapping_normalisation)
    if not ensemble_aimees:
        return 0.0

    ensemble_parfum = normaliser_notes(notes_parfum, mapping_normalisation)
    intersection = ensemble_aimees & ensemble_parfum
    return len(intersection) / len(ensemble_aimees)


def score_famille(famille_preferee, parfum):
    """
    1.0 si la famille DOMINANTE correspond à la famille préférée.
    0.5 si présent dans notes_categories.
    0.0 sinon.
    """
    if not famille_preferee:
        return 1.0
    famille_norm = str(famille_preferee).strip().lower()
    if famille_norm not in FAMILLES_CONNUES:
        raise ValueError(
            f"Famille inconnue : {famille_preferee!r}. Valeurs acceptées : {sorted(FAMILLES_CONNUES)}"
        )
    if parfum.get("famille") == famille_norm:
        return 1.0
    if famille_norm in parfum.get("notes_categories", []):
        return 0.5
    return 0.0


def score_saison(saison_demandee, parfum):
    """
    Réutilise directement le score saisonnier (winter_score, etc.).
    """
    if not saison_demandee:
        return 1.0
    saison_normalisee = _traduire(saison_demandee, TRADUCTION_SAISON, "saison")
    return float(parfum.get(f"{saison_normalisee}_score", 0.0))


def score_moment(moment_demande, parfum):
    """Même logique que score_saison sur day_score / night_score."""
    if not moment_demande:
        return 1.0
    moment_normalise = _traduire(moment_demande, TRADUCTION_MOMENT, "moment")
    return float(parfum.get(f"{moment_normalise}_score", 0.0))


def score_profil(profil_demande, parfum):
    """
    Compatibilité entre le profil demandé et celui du parfum.
    """
    if not profil_demande:
        return 1.0
    profil_normalise = _traduire(profil_demande, TRADUCTION_PROFIL, "profil")
    profil_parfum = str(parfum.get("profil", "")).strip().lower()
    
    # Sécurité au cas où la valeur dans le CSV est en FR (ex: "unisexe")
    if profil_parfum in TRADUCTION_PROFIL:
        profil_parfum = TRADUCTION_PROFIL[profil_parfum]

    return COMPATIBILITE_PROFIL.get((profil_normalise, profil_parfum), 0.0)


# ---------------------------------------------------------------------------
# Composition du score final
# ---------------------------------------------------------------------------
def calculer_score(preferences, parfum, mapping_normalisation, poids=POIDS_SCORING):
    """
    Calcule le score final d'un parfum pour des préférences données, ainsi
    que le détail (déjà pondéré) de chaque composante.

    Comporte un filtre de cohérence (pénalité multiplicative quadratique) si la saison 
    demandée est en opposition avec le parfum (< 0.50), évitant qu'un
    parfum d'hiver lourd ne sorte en été simplement grâce aux notes.
    """
    detail_brut = {
        "notes": score_similarite_notes(
            preferences.get("notes_aimees", []), parfum.get("notes_list", []), mapping_normalisation
        ),
        "famille": score_famille(preferences.get("famille_preferee"), parfum),
        "saison": score_saison(preferences.get("saison"), parfum),
        "moment": score_moment(preferences.get("moment"), parfum),
        "profil": score_profil(preferences.get("profil"), parfum),
    }

    # --- FILTRE ANTI-CONTRESENS SAISONNIER (Ajustement du seuil & Pente Quadratique) ---
    penalite_saison = 1.0
    if preferences.get("saison") and detail_brut["saison"] < 0.50:
        # Pente quadratique : un score saison de 0.42 subit un facteur de (0.42/0.50)^2 = ~0.7056
        penalite_saison = (detail_brut["saison"] / 0.50) ** 2

    # Application de la pénalité au dictionnaire de détails pour maintenir
    # une cohérence parfaite entre la somme des détails et score_final.
    detail_pondere = {
        composante: round(valeur * poids[composante] * penalite_saison, 4)
        for composante, valeur in detail_brut.items()
    }
    
    score_final = round(sum(detail_pondere.values()), 4)

    return {
        "nom": parfum.get("Name"),
        "marque": parfum.get("Brand"),
        "score_final": score_final,
        "details": detail_pondere,
    }


def recommander(preferences, parfums, mapping_normalisation, n=5, poids=POIDS_SCORING):
    """
    Fonction principale du moteur : calcule le score de chaque parfum
    et retourne les n meilleurs, triés par score décroissant.
    """
    marques_exclues = {str(m).strip().lower() for m in preferences.get("marques_exclues", [])}

    parfums_eligibles = [
        parfum for parfum in parfums
        if str(parfum.get("Brand", "")).strip().lower() not in marques_exclues
    ]

    resultats = [
        calculer_score(preferences, parfum, mapping_normalisation, poids)
        for parfum in parfums_eligibles
    ]
    resultats.sort(key=lambda r: r["score_final"], reverse=True)

    return resultats[:n]


# ---------------------------------------------------------------------------
# Chargement des données (I/O séparé des fonctions de scoring, qui restent pures)
# ---------------------------------------------------------------------------
def charger_knowledge_base(chemin_csv):
    """
    Charge la Nayaar Knowledge Base en liste de dicts.
    """
    with open(chemin_csv, encoding="utf-8") as f:
        parfums = list(csv.DictReader(f))
    for parfum in parfums:
        parfum["notes_list"] = json.loads(parfum.get("notes_list", "[]"))
        parfum["notes_categories"] = json.loads(parfum.get("notes_categories", "[]"))
    return parfums


def charger_mapping_normalisation(chemin_vocabulaire_json):
    """Charge le mapping de normalisation des notes depuis notes_vocabulary.json."""
    with open(chemin_vocabulaire_json, encoding="utf-8") as f:
        vocabulaire = json.load(f)
    return vocabulaire["mapping_normalisation"]


# ---------------------------------------------------------------------------
# Exemple d'utilisation
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    RACINE_PROJET = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    CHEMIN_KNOWLEDGE_BASE = os.path.join(RACINE_PROJET, "data", "processed", "nayaar_knowledge_base.csv")
    CHEMIN_VOCABULAIRE = os.path.join(RACINE_PROJET, "data", "processed", "notes_vocabulary.json")

    parfums = charger_knowledge_base(CHEMIN_KNOWLEDGE_BASE)
    mapping_normalisation = charger_mapping_normalisation(CHEMIN_VOCABULAIRE)

    # preferences_exemple = {
    #     "notes_aimees": ["Cinnamon", "amber", "musk", "vanilla", "Whiskey"],
    #     "famille_preferee": "boise",
    #     "saison": "Summer",
    #     "moment": "night",
    #     "profil": "Feminine",
    #     "marques_exclues": [],
    # }

#     preferences_exemple = { #Frais été test 1 
#     "notes_aimees": ["Lemon", "Bergamot", "Sea Salt", "Mint", "Cedar"],
#     "famille_preferee": "agrumes",
#     "saison": "Summer",
#     "moment": "day",
#     "profil": "Unisex",
#     "marques_exclues": [],
# }
    preferences_exemple = { #test 2
    "notes_aimees": ["Vanilla", "Tonka Bean", "Amber", "Cinnamon", "Rum"],
    "famille_preferee": "gourmand",
    "saison": "Winter",
    "moment": "night",
    "profil": "Feminine",
    "marques_exclues": [],
}

    top_5 = recommander(preferences_exemple, parfums, mapping_normalisation, n=5)

    print(f"Préférences : {preferences_exemple}\n")
    print(f"Top {len(top_5)} recommandations :\n")
    for rang, resultat in enumerate(top_5, start=1):
        print(f"{rang}. {resultat['nom']} — {resultat['marque']}")
        print(f"   score_final = {resultat['score_final']}")
        print(f"   details     = {resultat['details']}")
        print()