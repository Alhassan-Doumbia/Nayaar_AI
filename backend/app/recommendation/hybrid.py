# -*- coding: utf-8 -*-
"""
Recherche hybride Nayaar : sémantique + règles.

Ce module ne fait qu'ORCHESTRER deux moteurs indépendants, sans dupliquer
leur logique :
- semantic_search.py : trouve un pool de candidats par similarité de sens
  (FAISS sur les embeddings de profil_text).
- scoring.py : re-classe ce pool selon des préférences structurées, avec
  explication détaillée par composante.

Pipeline :
    requête en langage naturel
        -> pool de candidats (recherche sémantique)
        -> préférences structurées extraites par mots-clés (pas de GPT)
        -> re-classement du pool par le moteur de scoring
        -> combinaison pondérée des deux scores

Conforme à CLAUDE.md : aucun appel LLM ici, uniquement des règles
explicites. L'extraction de préférences par mots-clés est volontairement
simple (MVP) — elle ne remplace pas une compréhension fine du langage
naturel, elle sert juste à orienter le re-classement.
"""
import os

import scoring
import semantic_search

# ---------------------------------------------------------------------------
# Configuration — ajustable ici sans toucher au reste du code.
# ---------------------------------------------------------------------------
POIDS_HYBRIDE = {
    "semantique": 0.5,
    "regles": 0.5,
}
assert abs(sum(POIDS_HYBRIDE.values()) - 1.0) < 1e-9, "La somme des poids doit être égale à 1.0"
TAILLE_POOL_PAR_DEFAUT = 50  # nombre de candidats récupérés par la recherche sémantique avant re-classement

# Mots-clés (français + anglais) permettant de retrouver une famille
# olfactive dans une requête en langage naturel. Approche volontairement
# simple par sous-chaîne, pas de NLP avancé (pas de GPT à ce stade).
FAMILLE_MOTS_CLES = {
    "agrumes": ["agrume", "citron", "orange", "pamplemousse", "citrus", "bergamote"],
    "floral": ["floral", "fleur", "rose", "jasmin", "flowery"],
    "boise": ["boisé", "boise", "bois", "woody", "cèdre", "santal", "sandalwood"],
    "epice": ["épicé", "epice", "spicy", "poivre", "cannelle", "epices", "épices"],
    "oriental_ambre": ["ambré", "ambre", "oriental", "amber"],
    "aromatique": ["aromatique", "herbes", "lavande", "fougère"],
    "fruite": ["fruité", "fruite", "fruit", "fruity"],
    "gourmand": ["gourmand", "vanille", "sucré", "sweet", "dessert", "gourmande"],
    "musque": ["musqué", "musque", "musc", "musk"],
    "vert": ["vert", "green", "herbacé"],
    "aquatique": ["aquatique", "marin", "ocean", "océan", "aquatic"],
    "cuir": ["cuir", "leather"],
}


def extraire_preferences_du_texte(texte):
    """
    Extrait des préférences structurées (famille, saison, moment, profil)
    d'une requête en langage naturel, par simple recherche de mots-clés.
    Optimisé pour capturer plusieurs familles si elles sont mentionnées
    (ex: 'oriental boisé') sans casser la structure de retour.
    """
    texte_normalise = texte.lower()
    preferences = {}

    # Recherche de TOUTES les familles présentes dans le texte
    familles_detectees = []
    for famille, mots_cles in FAMILLE_MOTS_CLES.items():
        if any(mot in texte_normalise for mot in mots_cles):
            familles_detectees.append(famille)

    if familles_detectees:
        # S'il y a un combo comme "oriental" (oriental_ambre) et "boisé", 
        # on peut prioriser l'oriental ou l'ambre si présent, sinon on prend la première.
        # Ici, si "oriental_ambre" est présent parmi les détectés, on le choisit en priorité 
        # car il qualifie souvent l'ambiance globale, ou on garde le premier.
        if "oriental_ambre" in familles_detectees and "boise" in familles_detectees:
            preferences["famille_preferee"] = "oriental_ambre" # ou "boise" selon votre préférence, ou gérez un fallback
        else:
            preferences["famille_preferee"] = familles_detectees[0]

    for mot_cle, saison in scoring.TRADUCTION_SAISON.items():
        if mot_cle in texte_normalise:
            preferences["saison"] = saison
            break

    for mot_cle, moment in scoring.TRADUCTION_MOMENT.items():
        if mot_cle in texte_normalise:
            preferences["moment"] = moment
            break

    for mot_cle, profil in scoring.TRADUCTION_PROFIL.items():
        if mot_cle in texte_normalise:
            preferences["profil"] = profil
            break

    return preferences

# ---------------------------------------------------------------------------
# Chargement des ressources partagées (Knowledge Base + mapping de notes),
# une seule fois, réutilisées à chaque appel — même logique que le cache de
# semantic_search.py pour le modèle/index FAISS.
# ---------------------------------------------------------------------------
_parfums_par_cle = None
_mapping_normalisation = None


def _charger_ressources():
    """Charge la Knowledge Base (indexée par (nom, marque)) et le mapping de notes, une seule fois."""
    global _parfums_par_cle, _mapping_normalisation

    if _parfums_par_cle is None:
        racine_projet = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        chemin_knowledge_base = os.path.join(racine_projet, "data", "processed", "nayaar_knowledge_base.csv")
        parfums = scoring.charger_knowledge_base(chemin_knowledge_base)
        _parfums_par_cle = {(p["Name"], p["Brand"]): p for p in parfums}

    if _mapping_normalisation is None:
        racine_projet = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        chemin_vocabulaire = os.path.join(racine_projet, "data", "processed", "notes_vocabulary.json")
        _mapping_normalisation = scoring.charger_mapping_normalisation(chemin_vocabulaire)

    return _parfums_par_cle, _mapping_normalisation


def _distance_vers_similarite(distance):
    """
    Convertit une distance FAISS (L2 sur vecteurs normalisés, donc dans
    [0, 2] : 0 = identique, 2 = opposé) en une similarité dans [0, 1],
    directement comparable et combinable avec score_final de scoring.py
    (lui-même dans [0, 1]).
    """
    return max(0.0, 1.0 - distance / 2.0)


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------
def recherche_hybride(requete_texte, n_resultats=5, taille_pool=TAILLE_POOL_PAR_DEFAUT,
                       poids_hybride=POIDS_HYBRIDE, marques_exclues=None):
    """
    Combine recherche sémantique et moteur de scoring :
    1. La recherche sémantique (semantic_search.py) récupère taille_pool
       candidats proches du sens de la requête.
    2. Des préférences structurées sont extraites de la requête par
       mots-clés (famille, saison, moment, profil).
    3. Le moteur de scoring (scoring.py) note chaque candidat du pool selon
       ces préférences, avec le détail par composante.
    4. Le score final combine similarité sémantique et score de règles selon
       poids_hybride (0.4 / 0.6 par défaut).

    Retourne une liste de n_resultats dicts triés par score_hybride
    décroissant, chacun conservant l'explication complète :
    {nom, marque, famille, score_hybride, score_semantique,
     distance_semantique, score_regles, details_regles}.
    """
    parfums_par_cle, mapping_normalisation = _charger_ressources()

    candidats_semantiques = semantic_search.recherche_semantique(requete_texte, n=taille_pool)
    preferences = extraire_preferences_du_texte(requete_texte)
    if marques_exclues:
        preferences["marques_exclues"] = marques_exclues

    # On ne garde que les candidats retrouvables dans la Knowledge Base :
    # l'index FAISS et le CSV sont censés être synchronisés (même notebook
    # 04), un candidat introuvable signale une désynchronisation à corriger,
    # pas un cas à ignorer silencieusement.
    pool_parfums = []
    distance_par_cle = {}
    for candidat in candidats_semantiques:
        cle = (candidat["nom"], candidat["marque"])
        if cle not in parfums_par_cle:
            raise KeyError(
                f"Parfum {cle} retrouvé par la recherche sémantique mais absent de la "
                f"Knowledge Base — l'index FAISS (04_embeddings.ipynb) et "
                f"nayaar_knowledge_base.csv ne sont plus synchronisés."
            )
        pool_parfums.append(parfums_par_cle[cle])
        distance_par_cle[cle] = candidat["distance"]

    resultats_regles = scoring.recommander(
        preferences, pool_parfums, mapping_normalisation, n=len(pool_parfums)
    )

    resultats_hybrides = []
    for resultat_regles in resultats_regles:
        cle = (resultat_regles["nom"], resultat_regles["marque"])
        distance = distance_par_cle[cle]
        score_semantique = _distance_vers_similarite(distance)
        score_regles = resultat_regles["score_final"]

        score_hybride = round(
            poids_hybride["semantique"] * score_semantique + poids_hybride["regles"] * score_regles, 4
        )

        resultats_hybrides.append({
            "nom": resultat_regles["nom"],
            "marque": resultat_regles["marque"],
            "famille": parfums_par_cle[cle].get("famille"),
            "score_hybride": score_hybride,
            "score_semantique": round(score_semantique, 4),
            "distance_semantique": distance,
            "score_regles": score_regles,
            "details_regles": resultat_regles["details"],
        })

    resultats_hybrides.sort(key=lambda r: r["score_hybride"], reverse=True)
    return resultats_hybrides[:n_resultats]

def personal_testing():
    request=input("Enter your request: ")
    preferences_extraites = extraire_preferences_du_texte(request)
    print(f"Requête : {request!r}")
    print(f"Préférences extraites : {preferences_extraites}\n")
    for rang, resultat in enumerate(recherche_hybride(request, n_resultats=5), start=1):
                print(f"{rang}. {resultat['nom']} — {resultat['marque']} (famille : {resultat['famille']})")
                print(f"   score_hybride    = {resultat['score_hybride']}")
                print(f"   score_semantique = {resultat['score_semantique']} (distance brute : {resultat['distance_semantique']})")
                print(f"   score_regles     = {resultat['score_regles']}  détails : {resultat['details_regles']}")
                print()
    print("=" * 80)
    
if __name__ == "__main__":
    personal_testing()
    # requetes_exemple = [
    #     "un parfum élégant pour un mariage en été",
    #     "quelque chose de boisé et masculin pour le soir",
    # ]

    # for requete in requetes_exemple:
    #     preferences_extraites = extraire_preferences_du_texte(requete)
    #     print(f"Requête : {requete!r}")
    #     print(f"Préférences extraites : {preferences_extraites}\n")

    #     for rang, resultat in enumerate(recherche_hybride(requete, n_resultats=5), start=1):
    #         print(f"{rang}. {resultat['nom']} — {resultat['marque']} (famille : {resultat['famille']})")
    #         print(f"   score_hybride    = {resultat['score_hybride']}")
    #         print(f"   score_semantique = {resultat['score_semantique']} (distance brute : {resultat['distance_semantique']})")
    #         print(f"   score_regles     = {resultat['score_regles']}  détails : {resultat['details_regles']}")
    #         print()
    #     print("=" * 80)

