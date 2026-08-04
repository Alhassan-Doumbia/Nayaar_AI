# -*- coding: utf-8 -*-
"""
Recherche textuelle par nom/marque dans la Nayaar Knowledge Base.

Volontairement PAS de recherche sémantique ici (semantic_search.py) : quand
un client tape "sauvage" pour retrouver CE parfum précis, on veut le
parfum qui s'appelle Sauvage, pas des parfums "proches en ambiance". Une
correspondance de chaînes bien faite (insensible à la casse/aux accents,
tolérante aux fautes de frappe légères) suffit et reste rapide, sans
dépendance lourde (pas de modèle, pas d'index vectoriel).

Ce module ne charge JAMAIS la Knowledge Base lui-même : rechercher_par_nom
reçoit la liste déjà chargée en mémoire (voir routes/search.py, qui la
prend depuis request.app.state.parfums, chargée une seule fois au
démarrage de l'API — main.py).
"""
import unicodedata

# Niveaux de pertinence, du meilleur (0) au moins bon. Une correspondance
# exacte du nom ou de la marque prime toujours sur un simple "commence par",
# qui prime sur une simple sous-chaîne, qui prime sur une tolérance aux
# fautes de frappe (dernier recours).
TIER_EXACT = 0
TIER_DEBUT_DE_CHAINE = 1
TIER_SOUS_CHAINE = 2
TIER_APPROXIMATIF = 3


def normaliser(texte):
    """
    Minuscules + suppression des accents (é -> e, etc.), pour que "sauvage",
    "Sauvage" et "sauvagé" (faute de frappe sur l'accent) soient traités de
    façon identique. Même idiome que scoring.py (déduplication des notes).
    """
    if not texte:
        return ""
    texte = str(texte).strip().lower()
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(caractere for caractere in texte if not unicodedata.combining(caractere))


def _distance_levenshtein(a, b):
    """
    Distance d'édition (nombre minimal d'insertions/suppressions/substitutions
    pour passer de a à b). Implémentation légère, sans dépendance externe —
    volontairement en O(longueur_a * longueur_b), largement suffisant pour
    comparer des mots courts (noms de parfums, pas des textes longs).
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    ligne_precedente = list(range(len(b) + 1))
    for i, caractere_a in enumerate(a, start=1):
        ligne_courante = [i] + [0] * len(b)
        for j, caractere_b in enumerate(b, start=1):
            cout_substitution = 0 if caractere_a == caractere_b else 1
            ligne_courante[j] = min(
                ligne_precedente[j] + 1,  # suppression
                ligne_courante[j - 1] + 1,  # insertion
                ligne_precedente[j - 1] + cout_substitution,  # substitution
            )
        ligne_precedente = ligne_courante
    return ligne_precedente[-1]


def _tier_champ(requete_normalisee, champ_normalise):
    """Niveau de correspondance de la requête dans un champ donné (nom OU marque), ou None si aucune."""
    if not champ_normalise:
        return None
    if champ_normalise == requete_normalisee:
        return TIER_EXACT
    if champ_normalise.startswith(requete_normalisee):
        return TIER_DEBUT_DE_CHAINE
    if requete_normalisee in champ_normalise:
        return TIER_SOUS_CHAINE
    return None


def _tier_approximatif(requete_normalisee, nom_normalise, marque_normalise):
    """
    Tolérance aux petites fautes de frappe, en dernier recours (aucune
    correspondance exacte/préfixe/sous-chaîne trouvée). Compare la requête à
    chaque MOT du nom et de la marque (pas la chaîne entière : "savage"
    doit matcher le mot "sauvage" dans "Sauvage Eau de Toilette", pas
    échouer parce que le reste du titre allonge la distance).

    Requêtes de moins de 5 caractères ignorées : sur un mot court, une
    distance de 1 représente une trop grande part de la chaîne pour rester
    fiable (ex. "dior" (4 lettres) tombait à distance 1 de "d'or", présent
    dans plusieurs noms du catalogue — un faux positif trouvé en testant
    sur les vraies données, pas un cas théorique).
    """
    if len(requete_normalisee) < 5:
        return None

    tolerance = 1 if len(requete_normalisee) <= 6 else 2
    # .strip(ponctuation) : un mot collé à une parenthèse/virgule ("sauvage)",
    # "toilette,") ne doit pas être pénalisé sur sa longueur pour autant —
    # trouvé en testant sur un vrai titre du catalogue contenant "(...)".
    mots = [
        mot.strip(".,;:!?()[]\"'")
        for mot in (nom_normalise.split() + marque_normalise.split())
    ]
    for mot in mots:
        # filtre rapide avant de calculer la distance (évite du travail inutile)
        if abs(len(mot) - len(requete_normalisee)) > tolerance:
            continue
        if _distance_levenshtein(requete_normalisee, mot) <= tolerance:
            return TIER_APPROXIMATIF
    return None


def rechercher_par_nom(requete, parfums, limit=8):
    """
    Recherche textuelle sur les colonnes Name/Brand des parfums fournis
    (déjà chargés en mémoire par l'appelant). Retourne une liste de dicts
    {id, nom, marque, image_url}, triée par pertinence décroissante :
    correspondance exacte > début de chaîne > sous-chaîne > tolérance aux
    fautes de frappe.

    id = position du parfum dans la liste fournie, même convention que
    GET /api/perfumes/{id} et POST /api/layering (à condition que
    l'appelant passe la Knowledge Base dans le même ordre — c'est le cas
    de request.app.state.parfums, voir main.py).

    Retourne une liste vide si la requête est vide/blanche ou si rien ne
    correspond — jamais d'exception pour une recherche sans résultat.
    """
    requete_normalisee = normaliser(requete)
    if not requete_normalisee:
        return []

    correspondances = []
    for position, parfum in enumerate(parfums):
        nom_normalise = normaliser(parfum.get("Name", ""))
        marque_normalise = normaliser(parfum.get("Brand", ""))

        tier = _tier_champ(requete_normalisee, nom_normalise)
        tier_marque = _tier_champ(requete_normalisee, marque_normalise)
        if tier_marque is not None and (tier is None or tier_marque < tier):
            tier = tier_marque
        if tier is None:
            tier = _tier_approximatif(requete_normalisee, nom_normalise, marque_normalise)
        if tier is None:
            continue

        # à pertinence égale, on préfère le nom le plus court : une requête
        # qui matche "Sauvage" doit passer avant "Sauvage Elixir Extrait de Parfum"
        correspondances.append((tier, len(nom_normalise), position, parfum))

    correspondances.sort(key=lambda resultat: (resultat[0], resultat[1]))

    return [
        {
            "id": position,
            "nom": parfum.get("Name", ""),
            "marque": parfum.get("Brand", ""),
            "image_url": parfum.get("Image URL", ""),
        }
        for _, _, position, parfum in correspondances[:limit]
    ]


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(__file__))
    import scoring

    racine_projet = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    chemin_kb = os.path.join(racine_projet, "data", "processed", "nayaar_knowledge_base.csv")
    parfums = scoring.charger_knowledge_base(chemin_kb)

    requete_exemple = input("Recherche (nom ou marque) : ")
    resultats = rechercher_par_nom(requete_exemple, parfums)

    print(f"\n{len(resultats)} résultat(s) pour {requete_exemple!r} :\n")
    for resultat in resultats:
        print(f"  id={resultat['id']:4d}  {resultat['nom']} — {resultat['marque']}")
