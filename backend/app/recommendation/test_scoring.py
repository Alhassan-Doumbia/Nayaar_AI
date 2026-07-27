# -*- coding: utf-8 -*-
"""
Tests du moteur de scoring (scoring.py).

Les parfums utilisés ici sont des fixtures synthétiques construites à la
main (pas le vrai dataset) : on connaît d'avance le résultat exact attendu,
ce qui permet de vérifier que la formule de scoring est arithmétiquement
correcte, indépendamment de la qualité des données réelles.

Lancer avec : pytest backend/app/recommendation/test_scoring.py -v
"""
import pytest

from scoring import (
    POIDS_SCORING,
    calculer_score,
    recommander,
    score_famille,
    score_moment,
    score_profil,
    score_saison,
    score_similarite_notes,
)

# Mapping de normalisation minimal pour les tests (musks -> musk), le reste
# des tests n'a pas besoin de variantes d'écriture.
MAPPING_TEST = {"musks": "musk"}


def parfum_synthetique(**overrides):
    """
    Construit un parfum minimal avec des valeurs neutres par défaut, pour
    ne préciser dans chaque test que les champs réellement testés.
    """
    base = {
        "Name": "Parfum Test",
        "Brand": "Marque Test",
        "notes_list": [],
        "notes_categories": [],
        "famille": "",
        "winter_score": 0.5, "spring_score": 0.5, "summer_score": 0.5, "autumn_score": 0.5,
        "day_score": 0.5, "night_score": 0.5,
        "profil": "unisex",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Tests de la formule de scoring dans son ensemble
# ---------------------------------------------------------------------------
def test_score_parfait_avec_correspondance_totale():
    """Un parfum qui correspond exactement aux préférences doit obtenir le score maximum (1.0)."""
    parfum = parfum_synthetique(
        notes_list=["vanilla", "amber", "sandalwood"],
        famille="oriental_ambre",
        winter_score=1.0, night_score=1.0,
        profil="unisex",
    )
    preferences = {
        "notes_aimees": ["vanilla", "amber", "sandalwood"],
        "famille_preferee": "oriental_ambre",
        "saison": "winter",
        "moment": "night",
        "profil": "unisex",
    }

    resultat = calculer_score(preferences, parfum, MAPPING_TEST)

    assert resultat["score_final"] == 1.0
    assert resultat["details"] == {
        "notes": 0.35, "famille": 0.25, "saison": 0.20, "moment": 0.10, "profil": 0.10,
    }


def test_aucune_note_en_commun_donne_zero_sur_la_composante_notes():
    """Deux ensembles de notes disjoints doivent donner un rappel de 0, pas d'erreur."""
    parfum = parfum_synthetique(notes_list=["oud", "leather"])
    preferences = {"notes_aimees": ["vanilla", "peach"]}

    resultat = calculer_score(preferences, parfum, MAPPING_TEST)

    assert resultat["details"]["notes"] == 0.0


def test_preferences_vides_neutralisent_toutes_les_composantes_sauf_notes():
    """
    Sans aucune préférence exprimée (sauf notes_aimees, obligatoire), toutes
    les composantes doivent être neutres (poids plein), sauf 'notes' : un
    ensemble de notes aimées vide ne peut mathématiquement pas matcher.
    """
    parfum = parfum_synthetique(notes_list=["musk"])
    preferences = {"notes_aimees": []}

    resultat = calculer_score(preferences, parfum, MAPPING_TEST)

    assert resultat["details"]["notes"] == 0.0
    assert resultat["details"]["famille"] == POIDS_SCORING["famille"]
    assert resultat["details"]["saison"] == POIDS_SCORING["saison"]
    assert resultat["details"]["moment"] == POIDS_SCORING["moment"]
    assert resultat["details"]["profil"] == POIDS_SCORING["profil"]


def test_details_somment_toujours_au_score_final():
    """Invariant central du module : le détail pondéré doit toujours reconstituer le score final."""
    parfum = parfum_synthetique(notes_list=["rose", "musk"], famille="floral")
    preferences = {"notes_aimees": ["rose"], "famille_preferee": "floral", "saison": "spring"}

    resultat = calculer_score(preferences, parfum, MAPPING_TEST)

    assert resultat["score_final"] == pytest.approx(sum(resultat["details"].values()))


# ---------------------------------------------------------------------------
# Tests de chaque composante isolément
# ---------------------------------------------------------------------------
def test_similarite_notes_est_un_rappel_pas_un_jaccard():
    """
    Cas piège : un parfum "riche" (beaucoup de notes) qui contient pourtant
    TOUTES les notes demandées doit obtenir 1.0, pas être pénalisé par ses
    notes en plus (ce que ferait un indice de Jaccard classique).
    """
    resultat = score_similarite_notes(
        ["musk", "vanilla"],
        ["musk", "vanilla", "cedar", "amber", "oud", "leather", "rose", "iris"],
        MAPPING_TEST,
    )
    assert resultat == 1.0


def test_similarite_notes_rappel_partiel():
    """Cas connu à la main : intersection={musk}, notes_aimees={musk,amber} -> rappel = 1/2."""
    resultat = score_similarite_notes(["musk", "amber"], ["musk", "vanilla"], MAPPING_TEST)
    assert resultat == pytest.approx(1 / 2)


def test_similarite_notes_normalise_les_variantes_avant_comparaison():
    """'musks' (brut) et 'musk' (canonique demandé) doivent être reconnues comme la même note."""
    resultat = score_similarite_notes(["musk"], ["musks"], MAPPING_TEST)
    assert resultat == 1.0


def test_similarite_notes_insensible_a_la_casse():
    """'Cinnamon' (saisi par une couche amont) doit matcher 'cinnamon' (stocké en minuscules)."""
    resultat = score_similarite_notes(["Cinnamon", "Whiskey"], ["cinnamon", "whiskey"], MAPPING_TEST)
    assert resultat == 1.0


def test_famille_sans_preference_est_neutre():
    parfum = parfum_synthetique(famille="cuir")
    assert score_famille(None, parfum) == 1.0
    assert score_famille("", parfum) == 1.0


def test_famille_preference_qui_ne_correspond_pas_du_tout():
    """La famille demandée n'apparaît ni comme dominante, ni parmi les autres notes -> 0.0."""
    parfum = parfum_synthetique(famille="cuir", notes_categories=["cuir", "boise"])
    assert score_famille("floral", parfum) == 0.0


def test_famille_preference_partielle_via_notes_categories():
    """
    La famille demandée n'est pas la famille dominante, mais est quand même
    présente parmi les notes du parfum -> crédit partiel (0.5), pas 0.0.
    """
    parfum = parfum_synthetique(famille="floral", notes_categories=["floral", "boise", "musque"])
    assert score_famille("boise", parfum) == 0.5


def test_famille_inconnue_leve_une_erreur():
    """Une famille qui n'existe pas dans les 12 catégories doit échouer bruyamment, pas silencieusement."""
    parfum = parfum_synthetique(famille="floral")
    with pytest.raises(ValueError):
        score_famille("boisee", parfum)  # faute de frappe plausible


def test_saison_reprend_directement_le_score_du_parfum():
    """score_saison ne réinvente rien : il lit juste la colonne '{saison}_score' du parfum."""
    parfum = parfum_synthetique(summer_score=0.83)
    assert score_saison("summer", parfum) == 0.83
    assert score_saison(None, parfum) == 1.0  # neutre si pas demandé


def test_saison_accepte_le_francais():
    """'été' doit être traduit vers summer_score, sans quoi le score serait silencieusement 0.0."""
    parfum = parfum_synthetique(summer_score=0.83, winter_score=0.1)
    assert score_saison("été", parfum) == 0.83
    assert score_saison("hiver", parfum) == 0.1


def test_saison_inconnue_leve_une_erreur():
    parfum = parfum_synthetique()
    with pytest.raises(ValueError):
        score_saison("nimportequoi", parfum)


def test_moment_reprend_directement_le_score_du_parfum():
    parfum = parfum_synthetique(day_score=0.2, night_score=0.9)
    assert score_moment("day", parfum) == 0.2
    assert score_moment("night", parfum) == 0.9
    assert score_moment("nuit", parfum) == 0.9  # français accepté


@pytest.mark.parametrize(
    "profil_demande, profil_parfum, score_attendu",
    [
        ("masculine", "masculine", 1.0),
        ("masculine", "unisex", 0.5),
        ("masculine", "feminine", 0.0),
        ("feminine", "feminine", 1.0),
        ("feminine", "unisex", 0.5),
        ("unisex", "unisex", 1.0),
        ("unisex", "masculine", 0.0),
        ("féminin", "feminine", 1.0),  # français accepté
        ("masculin", "unisex", 0.5),
    ],
)
def test_compatibilite_profil(profil_demande, profil_parfum, score_attendu):
    """Vérifie toute la table de compatibilité profil demandé <-> profil du parfum, FR et EN."""
    parfum = parfum_synthetique(profil=profil_parfum)
    assert score_profil(profil_demande, parfum) == score_attendu


def test_profil_inconnu_leve_une_erreur():
    parfum = parfum_synthetique()
    with pytest.raises(ValueError):
        score_profil("androgyne", parfum)


# ---------------------------------------------------------------------------
# Tests de la fonction recommander (filtrage + tri)
# ---------------------------------------------------------------------------
def test_recommander_exclut_les_marques_indesirees():
    parfums = [
        parfum_synthetique(Name="A", Brand="Chanel", notes_list=["musk"]),
        parfum_synthetique(Name="B", Brand="Dior", notes_list=["musk"]),
    ]
    preferences = {"notes_aimees": ["musk"], "marques_exclues": ["Chanel"]}

    resultats = recommander(preferences, parfums, MAPPING_TEST, n=10)

    marques_retournees = {r["marque"] for r in resultats}
    assert marques_retournees == {"Dior"}


def test_recommander_trie_par_score_decroissant():
    parfums = [
        parfum_synthetique(Name="Faible match", Brand="X", notes_list=["oud"]),
        parfum_synthetique(Name="Bon match", Brand="Y", notes_list=["musk", "vanilla"]),
    ]
    preferences = {"notes_aimees": ["musk", "vanilla"]}

    resultats = recommander(preferences, parfums, MAPPING_TEST, n=10)

    assert resultats[0]["nom"] == "Bon match"
    assert resultats[0]["score_final"] >= resultats[1]["score_final"]


def test_recommander_respecte_la_limite_n():
    parfums = [parfum_synthetique(Name=f"Parfum {i}", Brand=f"Marque {i}") for i in range(10)]
    preferences = {"notes_aimees": ["musk"]}

    resultats = recommander(preferences, parfums, MAPPING_TEST, n=3)

    assert len(resultats) == 3


# ---------------------------------------------------------------------------
# Test de configuration
# ---------------------------------------------------------------------------
def test_poids_scoring_somme_a_un():
    """Documente et verrouille l'invariant déjà vérifié par assert au chargement du module."""
    assert sum(POIDS_SCORING.values()) == pytest.approx(1.0)
