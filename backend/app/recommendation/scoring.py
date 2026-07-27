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
# de la Knowledge Base (winter_score, day_score, profil...). Toute valeur
# absente de ces tables déclenche une erreur explicite (voir _traduire) au
# lieu de faire silencieusement échouer le scoring sur TOUS les parfums
# (un f"{cle}_score" introuvable renverrait 0.0 partout sans prévenir).
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
    la clé interne utilisée par la Knowledge Base. Lève une erreur explicite
    si la valeur n'est reconnue dans aucune langue, plutôt que de laisser le
    scoring continuer avec une clé invalide qui produirait un score neutre
    de 0.0 sur tous les parfums sans que personne ne s'en aperçoive.
    """
    traduction = table_traduction.get(valeur.strip().lower())
    if traduction is None:
        raise ValueError(
            f"Valeur inconnue pour {nom_champ!r} : {valeur!r}. "
            f"Valeurs acceptées : {sorted(set(table_traduction))}"
        )
    return traduction


# Compatibilité entre le profil demandé et le profil du parfum. Un parfum
# unisexe convient partiellement à une demande genrée (et inversement), mais
# un parfum genré ne convient pas à une demande de l'autre genre. Explicite
# plutôt qu'un enchaînement de if/else difficile à auditer.
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
    Normalise une liste de notes brutes en un ensemble de notes canoniques :
    mise en minuscules (le vocabulaire et les notes stockées sont tous en
    minuscules, mais rien ne garantit que les notes_aimees envoyées par une
    couche amont le soient — "Cinnamon" doit matcher "cinnamon") puis mapping
    via le même dictionnaire que les notebooks 03a/03b (notes_vocabulary.json
    -> "mapping_normalisation"), pour que "musks" et "musk" soient reconnues
    comme identiques.
    """
    resultat = set()
    for note in notes_brutes:
        note_minuscule = note.strip().lower()
        resultat.add(mapping_normalisation.get(note_minuscule, note_minuscule))
    return resultat


def score_similarite_notes(notes_aimees, notes_parfum, mapping_normalisation):
    """
    Taux de rappel (recall) des notes aimées par l'utilisateur dans les notes
    du parfum : taille de l'intersection / taille de l'ensemble des notes
    aimées, après normalisation des deux côtés.

    Volontairement PAS un indice de Jaccard (intersection / union) : avec
    Jaccard, un parfum riche en notes (ex. 15 notes) qui contient pourtant
    EXACTEMENT les 2 notes demandées seraient pénalisé (score 2/15 = 0.13)
    par rapport à un parfum minimaliste. Avec le rappel, un parfum qui
    contient toutes les notes demandées obtient 1.0, peu importe le nombre
    d'autres notes qu'il contient en plus — c'est bien "l'utilisateur a-t-il
    trouvé ce qu'il voulait ?" qu'on mesure, pas "les deux listes se
    ressemblent-elles globalement ?".

    Retourne 0.0 si l'utilisateur n'a demandé aucune note (rien à mesurer).
    """
    ensemble_aimees = normaliser_notes(notes_aimees, mapping_normalisation)
    if not ensemble_aimees:
        return 0.0

    ensemble_parfum = normaliser_notes(notes_parfum, mapping_normalisation)
    intersection = ensemble_aimees & ensemble_parfum
    return len(intersection) / len(ensemble_aimees)


def score_famille(famille_preferee, parfum):
    """
    1.0 si la famille DOMINANTE du parfum correspond à la famille préférée.
    0.5 si elle ne domine pas mais est quand même présente parmi les notes du
    parfum (colonne notes_categories, notebook 03b) : un parfum "floral" qui
    contient aussi des notes boisées ne doit pas être aussi mal noté qu'un
    parfum entièrement floral pour quelqu'un qui cherche du boisé — sans
    quoi la composante famille est trop binaire pour des parfums composites.
    0.0 si la famille préférée n'apparaît nulle part dans le parfum.
    Si l'utilisateur n'a pas exprimé de préférence, la composante est neutre
    (1.0) : elle ne doit pas pénaliser un critère non demandé.
    """
    if not famille_preferee:
        return 1.0
    if famille_preferee not in FAMILLES_CONNUES:
        raise ValueError(
            f"Famille inconnue : {famille_preferee!r}. Valeurs acceptées : {sorted(FAMILLES_CONNUES)}"
        )
    if parfum.get("famille") == famille_preferee:
        return 1.0
    if famille_preferee in parfum.get("notes_categories", []):
        return 0.5
    return 0.0


def score_saison(saison_demandee, parfum):
    """
    Réutilise directement le score saisonnier déjà calculé sur le parfum
    (winter_score, spring_score, summer_score, autumn_score - notebook 03b) :
    c'est littéralement "à quel point ce parfum convient à cette saison".
    Accepte le français ou l'anglais (voir TRADUCTION_SAISON) et lève une
    erreur si la valeur n'est reconnue dans aucun des deux : un mot non
    traduit (ex. "été" envoyé tel quel par une couche de parsing amont)
    produirait sinon une clé "été_score" absente du parfum, donc un score de
    0.0 silencieux pour absolument tous les parfums.
    Neutre (1.0) si aucune saison n'est demandée.
    """
    if not saison_demandee:
        return 1.0
    saison_normalisee = _traduire(saison_demandee, TRADUCTION_SAISON, "saison")
    return float(parfum.get(f"{saison_normalisee}_score", 0.0))


def score_moment(moment_demande, parfum):
    """Même logique que score_saison (avec les mêmes garde-fous), sur day_score / night_score."""
    if not moment_demande:
        return 1.0
    moment_normalise = _traduire(moment_demande, TRADUCTION_MOMENT, "moment")
    return float(parfum.get(f"{moment_normalise}_score", 0.0))


def score_profil(profil_demande, parfum):
    """
    Compatibilité entre le profil demandé et celui du parfum, via la table
    COMPATIBILITE_PROFIL (un parfum unisexe convient partiellement à une
    demande genrée). Accepte le français ou l'anglais. Neutre (1.0) si aucun
    profil n'est demandé.
    """
    if not profil_demande:
        return 1.0
    profil_normalise = _traduire(profil_demande, TRADUCTION_PROFIL, "profil")
    profil_parfum = parfum.get("profil")
    return COMPATIBILITE_PROFIL.get((profil_normalise, profil_parfum), 0.0)


# ---------------------------------------------------------------------------
# Composition du score final
# ---------------------------------------------------------------------------
def calculer_score(preferences, parfum, mapping_normalisation, poids=POIDS_SCORING):
    """
    Calcule le score final d'un parfum pour des préférences données, ainsi
    que le détail (déjà pondéré) de chaque composante. C'est ce détail qui
    permet d'expliquer n'importe quelle recommandation.

    preferences : dict avec les clés notes_aimees, famille_preferee, saison,
                  moment, profil (toutes optionnelles sauf notes_aimees).
    parfum : dict représentant une ligne de la Knowledge Base (doit contenir
             au moins notes_list, notes_categories, famille, *_score, profil,
             Name, Brand).
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

    # Le détail exposé est déjà pondéré : la somme des valeurs de "details"
    # est exactement égale à score_final, ce qui rend l'explication directe
    # ("ce parfum a eu 0.28 sur 0.35 possibles grâce à ses notes").
    detail_pondere = {
        composante: round(valeur * poids[composante], 4)
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
    (en excluant les marques de preferences["marques_exclues"]) et retourne
    les n meilleurs, triés par score décroissant.
    """
    marques_exclues = {m.lower() for m in preferences.get("marques_exclues", [])}

    parfums_eligibles = [
        parfum for parfum in parfums
        if parfum.get("Brand", "").lower() not in marques_exclues
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
    Charge la Nayaar Knowledge Base en liste de dicts. notes_list et
    notes_categories sont désérialisées (stockées en JSON dans le CSV,
    notebook 03b) : notes_list pour score_similarite_notes, notes_categories
    pour le crédit partiel de score_famille.
    """
    with open(chemin_csv, encoding="utf-8") as f:
        parfums = list(csv.DictReader(f))
    for parfum in parfums:
        parfum["notes_list"] = json.loads(parfum["notes_list"])
        parfum["notes_categories"] = json.loads(parfum["notes_categories"])
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

    preferences_exemple = {
        "notes_aimees": ["Cinnamon", "amber", "musk","vanilla","Whiskey"],
        "famille_preferee": "boise",
        "saison": "Summer",
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
