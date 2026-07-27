# -*- coding: utf-8 -*-
"""
Recherche sémantique Nayaar.

Encode une requête en langage naturel avec le même modèle que le notebook
04 (all-MiniLM-L6-v2), interroge l'index FAISS construit sur profil_text, et
retourne les parfums les plus proches avec leur distance.

FAISS tourne en local (pas de base vectorielle externe au MVP, voir
Docs/MVP_SCOPE.md). Ce module n'est qu'une couche de recherche par sens :
il ne décide de rien — c'est le moteur de scoring (scoring.py) qui applique
les règles métier. Conforme à CLAUDE.md : l'IA ne décide jamais seule.
"""
import json
import os

import faiss
from sentence_transformers import SentenceTransformer

RACINE_PROJET = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CHEMIN_INDEX_FAISS = os.path.join(RACINE_PROJET, "data", "processed", "nayaar_index.faiss")
CHEMIN_MAPPING = os.path.join(RACINE_PROJET, "data", "processed", "nayaar_index_mapping.json")

NOM_MODELE = "all-MiniLM-L6-v2"  # doit rester identique au modèle utilisé pour construire l'index

# Ressources coûteuses à charger (modèle ~80 Mo, index vectoriel) : chargées
# une seule fois en mémoire au premier appel, puis réutilisées. Ce sont les
# seules variables globales du module, justifiées par ce besoin de cache.
_modele = None
_index = None
_mapping = None


def _charger_ressources():
    """
    Charge le modèle d'embeddings, l'index FAISS et le mapping position ->
    parfum, uniquement s'ils ne sont pas déjà en mémoire. Toute la logique
    de "charger une seule fois" est centralisée ici plutôt que dispersée.
    """
    global _modele, _index, _mapping

    if _modele is None:
        _modele = SentenceTransformer(NOM_MODELE)

    if _index is None:
        _index = faiss.read_index(CHEMIN_INDEX_FAISS)

    if _mapping is None:
        with open(CHEMIN_MAPPING, encoding="utf-8") as f:
            _mapping = json.load(f)

    return _modele, _index, _mapping


def recherche_semantique(requete_texte, n=5):
    """
    Encode une requête en langage naturel et retourne les n parfums dont le
    profil_text est le plus proche sémantiquement, triés par distance
    croissante (0 = identique).

    Retourne une liste de dicts : {nom, marque, famille, distance}.
    """
    modele, index, mapping = _charger_ressources()

    vecteur_requete = modele.encode(
        [requete_texte],
        convert_to_numpy=True,
        normalize_embeddings=True,  # même normalisation qu'au moment de l'indexation (notebook 04)
    ).astype("float32")

    distances, positions = index.search(vecteur_requete, n)

    resultats = []
    for distance, position in zip(distances[0], positions[0]):
        if position == -1:
            continue  # FAISS retourne -1 si l'index contient moins de n vecteurs
        parfum = mapping[position]
        resultats.append({
            "nom": parfum["nom"],
            "marque": parfum["marque"],
            "famille": parfum["famille"],
            "distance": round(float(distance), 4),
        })

    return resultats

# for my personal testing 

def testing():
    request=str(input("Enter your request: "))
    for rang, resultat in enumerate(recherche_semantique(request, n=5), start=1):
            print(f"  {rang}. {resultat['nom']} — {resultat['marque']} "f"(famille : {resultat['famille']}, distance : {resultat['distance']})")
            print()
if __name__ == "__main__":
    # requetes_exemple = [
    #     "un parfum boisé et chaud pour l'hiver",
    #     "quelque chose de frais et léger pour l'été",
    #     "un parfum floral et féminin pour le jour",
    # ]

    # for requete in requetes_exemple:
    #     print(f"Requête : {requete!r}\n")
    #     for rang, resultat in enumerate(recherche_semantique(requete, n=5), start=1):
    #         print(f"  {rang}. {resultat['nom']} — {resultat['marque']} "
    #               f"(famille : {resultat['famille']}, distance : {resultat['distance']})")
    #     print()
    testing()

