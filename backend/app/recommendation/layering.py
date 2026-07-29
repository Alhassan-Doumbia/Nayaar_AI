# -*- coding: utf-8 -*-
"""
Moteur de layering Nayaar — v1 heuristique, règles métier uniquement.

Pour un parfum donné, propose les N parfums de la Knowledge Base les plus
compatibles pour une superposition (layering), avec un score de
compatibilité explicable, le détail des contributions, et un ordre
d'application suggéré (lequel porter en base, lequel porter au-dessus).

Travaille exclusivement sur la Nayaar Knowledge Base (aucune source
externe). Conforme à CLAUDE.md : aucun appel LLM ici, uniquement des règles
explicites, pures et testables — comme scoring.py, dont ce module réutilise
le chargement de la Knowledge Base (scoring.charger_knowledge_base).
"""
import scoring

# ---------------------------------------------------------------------------
# Configuration des poids — ajustable ici sans toucher au reste du code.
# ---------------------------------------------------------------------------
POIDS_LAYERING = {
    "categories": 0.35,       # les familles olfactives des deux parfums se marient-elles ?
    "complementarite": 0.25,  # le candidat apporte-t-il des catégories nouvelles, ou redondantes ?
    "saison_moment": 0.25,    # les deux parfums sont-ils pensés pour les mêmes contextes ?
    "profil": 0.15,           # les profils (masculin/féminin/unisexe) sont-ils compatibles ?
}
assert abs(sum(POIDS_LAYERING.values()) - 1.0) < 1e-9, "La somme des poids doit être égale à 1.0"

# ---------------------------------------------------------------------------
# Matrice de compatibilité entre familles olfactives.
#
# Volontairement PETITE et éditable à la main : seules les associations
# notoirement excellentes ou notoirement dissonantes en parfumerie sont
# listées explicitement (clé = les deux familles, ordre indifférent).
# Toute paire absente de cette liste retombe sur SCORE_PAIRE_PAR_DEFAUT
# (ni conflit ni synergie connue) plutôt que d'inventer une valeur.
# ---------------------------------------------------------------------------
MATRICE_COMPATIBILITE_CATEGORIES = {
    # associations qui se marient bien (mariages classiques en parfumerie)
    frozenset(["gourmand", "boise"]): 0.90,
    frozenset(["floral", "musque"]): 0.90,
    frozenset(["oriental_ambre", "epice"]): 0.90,
    frozenset(["agrumes", "aromatique"]): 0.85,
    frozenset(["cuir", "oriental_ambre"]): 0.85,
    frozenset(["musque", "boise"]): 0.80,
    frozenset(["cuir", "boise"]): 0.80,
    frozenset(["agrumes", "boise"]): 0.75,
    frozenset(["vert", "aromatique"]): 0.75,
    frozenset(["epice", "boise"]): 0.75,
    frozenset(["floral", "boise"]): 0.75,
    frozenset(["aquatique", "agrumes"]): 0.75,
    frozenset(["cuir", "epice"]): 0.75,
    frozenset(["floral", "agrumes"]): 0.70,
    frozenset(["floral", "vert"]): 0.70,
    frozenset(["fruite", "gourmand"]): 0.70,
    frozenset(["musque", "cuir"]): 0.70,
    frozenset(["boise", "aromatique"]): 0.70,
    # associations qui se heurtent (clash olfactif reconnu)
    frozenset(["aquatique", "gourmand"]): 0.20,
    frozenset(["aquatique", "oriental_ambre"]): 0.25,
    frozenset(["aquatique", "cuir"]): 0.30,
    frozenset(["vert", "gourmand"]): 0.30,
    frozenset(["epice", "aquatique"]): 0.30,
    frozenset(["fruite", "cuir"]): 0.35,
    frozenset(["oriental_ambre", "vert"]): 0.40,
}
SCORE_PAIRE_PAR_DEFAUT = 0.55  # aucune synergie ni conflit répertorié : neutre
SCORE_MEME_CATEGORIE = 0.55    # deux parfums de même famille dominante : cohérent mais peu complémentaire (voir "complementarite")


def score_categories(famille_reference, famille_candidat):
    """
    Compatibilité entre les deux familles olfactives dominantes, via
    MATRICE_COMPATIBILITE_CATEGORIES. Neutre si l'une des deux familles est
    inconnue (parfum sans note reconnue par le vocabulaire, voir notebook 03b).
    """
    if not famille_reference or not famille_candidat:
        return SCORE_PAIRE_PAR_DEFAUT
    if famille_reference == famille_candidat:
        return SCORE_MEME_CATEGORIE
    paire = frozenset([famille_reference, famille_candidat])
    return MATRICE_COMPATIBILITE_CATEGORIES.get(paire, SCORE_PAIRE_PAR_DEFAUT)


def score_complementarite(categories_reference, categories_candidat):
    """
    Récompense un candidat qui apporte des catégories ABSENTES du parfum de
    référence (diversité utile pour un layering : chaque parfum apporte
    quelque chose), pénalise la redondance totale (mêmes catégories des deux
    côtés -> le candidat n'ajoute rien de nouveau à la superposition).

    Score = proportion des catégories du candidat qui sont nouvelles par
    rapport à la référence (1.0 = toutes nouvelles, 0.0 = aucune nouvelle).
    """
    ensemble_candidat = set(categories_candidat)
    if not ensemble_candidat:
        return 0.5  # candidat sans catégorie reconnue : ni bon ni mauvais signal
    ensemble_reference = set(categories_reference)
    categories_nouvelles = ensemble_candidat - ensemble_reference
    return round(len(categories_nouvelles) / len(ensemble_candidat), 4)


def score_coherence_saison_moment(reference, candidat):
    """
    Compare les profils saisonniers (winter/spring/summer/autumn_score) et
    de moment (day_score) des deux parfums : plus leurs scores se
    ressemblent, plus ils sont cohérents à porter ensemble. Pénalise par
    exemple un parfum estival très léger associé à un parfum hivernal très
    lourd (leurs scores saisonniers seraient à l'opposé l'un de l'autre).
    """
    cles_saison = ["winter_score", "spring_score", "summer_score", "autumn_score"]
    ecarts_saison = [
        abs(float(reference[cle]) - float(candidat[cle])) for cle in cles_saison
    ]
    coherence_saison = 1 - (sum(ecarts_saison) / len(ecarts_saison))

    ecart_moment = abs(float(reference["day_score"]) - float(candidat["day_score"]))
    coherence_moment = 1 - ecart_moment

    return round((coherence_saison + coherence_moment) / 2, 4)


# Compatibilité entre profils pour un layering : deux profils identiques ou
# un profil unisexe avec un profil genré restent cohérents ; deux profils
# genrés opposés (masculin/féminin) sont jugés plus dissonants pour une
# association, sans être exclus (0.4, pas 0).
COMPATIBILITE_PROFIL_LAYERING = {
    frozenset(["masculine"]): 1.0,
    frozenset(["feminine"]): 1.0,
    frozenset(["unisex"]): 1.0,
    frozenset(["masculine", "unisex"]): 0.8,
    frozenset(["feminine", "unisex"]): 0.8,
    frozenset(["masculine", "feminine"]): 0.4,
}


def score_coherence_profil(profil_reference, profil_candidat):
    """Compatibilité entre les profils des deux parfums, via COMPATIBILITE_PROFIL_LAYERING."""
    if not profil_reference or not profil_candidat:
        return 0.5
    return COMPATIBILITE_PROFIL_LAYERING.get(
        frozenset([profil_reference, profil_candidat]), 0.5
    )


def calculer_compatibilite(reference, candidat):
    """
    Calcule le score de compatibilité de layering entre deux parfums, ainsi
    que le détail (déjà pondéré) de chaque composante — c'est ce détail qui
    permet d'expliquer pourquoi deux parfums sont jugés compatibles.
    """
    detail_brut = {
        "categories": score_categories(reference.get("famille"), candidat.get("famille")),
        "complementarite": score_complementarite(
            reference.get("notes_categories", []), candidat.get("notes_categories", [])
        ),
        "saison_moment": score_coherence_saison_moment(reference, candidat),
        "profil": score_coherence_profil(reference.get("profil"), candidat.get("profil")),
    }
    detail_pondere = {
        composante: round(valeur * POIDS_LAYERING[composante], 4)
        for composante, valeur in detail_brut.items()
    }
    score_final = round(sum(detail_pondere.values()), 4)
    return {"score_final": score_final, "details": detail_pondere}


# ---------------------------------------------------------------------------
# Ordre d'application : le parfum le plus "lourd" (ambré/boisé/hivernal, à
# tenue longue) se porte en base, le plus "léger" (frais/volatil/estival)
# se porte au-dessus. Heuristique combinant le score hiver (plus il est
# élevé, plus le parfum est associé à des matières lourdes), l'inverse du
# score été, et un bonus/malus pour les familles notoirement lourdes/légères.
# ---------------------------------------------------------------------------
FAMILLES_LOURDES = {"oriental_ambre", "boise", "cuir", "gourmand", "musque"}
FAMILLES_LEGERES = {"agrumes", "aquatique", "vert"}


def calculer_score_lourdeur(parfum):
    """
    Score relatif de "lourdeur" olfactive d'un parfum, utilisé uniquement
    pour comparer deux parfums entre eux (pas une échelle absolue). Plus il
    est élevé, plus le parfum est associé à une tenue longue et une
    présence marquée (ambré, boisé, hivernal).
    """
    score = float(parfum["winter_score"]) * 0.5 + (1 - float(parfum["summer_score"])) * 0.3
    famille = parfum.get("famille")
    if famille in FAMILLES_LOURDES:
        score += 0.2
    elif famille in FAMILLES_LEGERES:
        score -= 0.2
    return score


def determiner_role(lourdeur_reference, lourdeur_candidat):
    """Le plus lourd des deux va en base, l'autre se porte au-dessus."""
    return "base" if lourdeur_candidat >= lourdeur_reference else "dessus"


# ---------------------------------------------------------------------------
# Chargement de la Knowledge Base (I/O séparé du calcul, qui reste pur) —
# même mécanique de cache que hybrid.py / semantic_search.py : chargée une
# seule fois, réutilisée à chaque appel.
# ---------------------------------------------------------------------------
_parfums_cache = None


def _charger_parfums():
    """Charge la Knowledge Base une seule fois (voir scoring.charger_knowledge_base)."""
    global _parfums_cache
    if _parfums_cache is None:
        import os

        racine_projet = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        chemin_defaut = os.path.join(racine_projet, "data", "processed", "nayaar_knowledge_base.csv")
        chemin = os.environ.get("NAYAAR_KNOWLEDGE_BASE_PATH") or chemin_defaut
        if not os.path.isabs(chemin):
            chemin = os.path.join(racine_projet, chemin)
        _parfums_cache = scoring.charger_knowledge_base(chemin)
    return _parfums_cache


def proposer_layering(perfume_id, n=3, parfums=None):
    """
    Fonction principale du moteur : pour le parfum situé à l'index
    perfume_id dans la Knowledge Base (même convention d'id que
    GET /api/perfumes/{id} : la position dans le CSV), retourne les n
    parfums les plus compatibles pour un layering.

    parfums : liste de parfums à utiliser (permet de passer des fixtures
    synthétiques en test) ; si None, charge la Knowledge Base réelle.

    Retourne une liste de dicts triés par score_compatibilite décroissant :
    {nom, marque, image_url, score_compatibilite, details, role}
    role vaut "base" (à porter en dessous) ou "dessus" (à porter par-dessus)
    par rapport au parfum de référence.
    """
    if parfums is None:
        parfums = _charger_parfums()

    if perfume_id < 0 or perfume_id >= len(parfums):
        raise IndexError(
            f"Aucun parfum avec l'id {perfume_id} (Knowledge Base : {len(parfums)} parfums)."
        )

    reference = parfums[perfume_id]
    lourdeur_reference = calculer_score_lourdeur(reference)

    resultats = []
    for position, candidat in enumerate(parfums):
        if position == perfume_id:
            continue  # on exclut le parfum lui-même des propositions

        compatibilite = calculer_compatibilite(reference, candidat)
        role = determiner_role(lourdeur_reference, calculer_score_lourdeur(candidat))

        resultats.append({
            "nom": candidat["Name"],
            "marque": candidat["Brand"],
            "image_url": candidat.get("Image URL", ""),
            "score_compatibilite": compatibilite["score_final"],
            "details": compatibilite["details"],
            "role": role,
        })

    resultats.sort(key=lambda r: r["score_compatibilite"], reverse=True)
    return resultats[:n]


if __name__ == "__main__":
    parfums = _charger_parfums()

    id_exemple = int(input(f"Entrez l'id du parfum de référence (0 à {len(parfums)-1}) : "))
    print(f"Parfum de référence : {parfums[id_exemple]['Name']} — {parfums[id_exemple]['Brand']}")
    print(f"Famille : {parfums[id_exemple]['famille']}\n")

    propositions = proposer_layering(id_exemple, n=3, parfums=parfums)

    print(f"Top {len(propositions)} propositions de layering :\n")
    for rang, proposition in enumerate(propositions, start=1):
        print(f"{rang}. {proposition['nom']} — {proposition['marque']}  (à porter en {proposition['role']})")
        print(f"   score_compatibilite = {proposition['score_compatibilite']}")
        print(f"   details             = {proposition['details']}")
        print()
