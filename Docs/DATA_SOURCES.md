# DATA SOURCES
# Nayaar Knowledge Graph

Version : 1.1

---

# Objectif

Ce document recense toutes les sources de données utilisées pour construire
le Nayaar Knowledge Graph, et précise le rôle exact de chacune.

Le projet repose sur UNE seule source réellement exploitable techniquement
(Kaggle). Les autres sources sont des références documentaires manuelles,
utilisées par le porteur du projet pour vérifier et concevoir — jamais
dans le code du MVP.

La base propriétaire finale est appelée **Nayaar Knowledge Base**.

---

# Architecture générale (MVP)

Source unique (Kaggle)
        ↓
      Import
        ↓
    Nettoyage
        ↓
  Normalisation
        ↓
Feature Engineering (dérivé du texte + assisté par IA)
        ↓
    Validation
        ↓
Nayaar Knowledge Base
        ↓
   Embeddings
        ↓
 Knowledge Graph
        ↓
      RAG
        ↓
Application Nayaar

> Note : il n'y a PAS de fusion multi-sources au MVP.
> La fusion de plusieurs bases est une ambition v2+ (voir ROADMAP).

---

# Source 1 — Dataset principal (SEULE source du pipeline)

## Kaggle Perfume Recommendation Dataset

Statut : ✅ Source principale et unique du MVP.

Lien : https://www.kaggle.com/datasets/nandini1999/perfume-recommendation-dataset

Contenu réel (~2 191 parfums) :

- nom
- marque
- description (texte libre)
- notes (texte libre)
- image (URL)

⚠️ Important : ce dataset NE contient PAS de famille olfactive,
de sous-famille, de notes séparées tête/cœur/fond, d'accords structurés,
ni de concentration. Tout cela devra être dérivé ou généré (voir plus bas).

Ces données sont la vérité de référence et restent immuables.

---

## Structure réelle confirmée du fichier brut (notebooks 01/02)

Fichier : `data/raw/final_perfume_data.csv.zip` (CSV unique dans l'archive,
jamais extrait sur disque — lu directement depuis le zip).

Colonnes réelles (noms exacts, sensibles à la casse) :

- `Name`
- `Brand`
- `Description`
- `Notes`
- `Image URL`

Volumétrie : 2191 lignes.

⚠️ **Encodage : `latin-1`, pas UTF-8.** Le fichier échoue en décodage UTF-8
strict (octet invalide) et en `cp1252` strict (octet non mappé). `latin-1` est
l'encodage à utiliser pour le lire sans erreur ni perte de caractères.

**Colonne `Notes`** : texte libre, notes séparées par des virgules, **sans
structure tête / cœur / fond** (ex. `"Vanilla bean, musks"`). 80 lignes
(~3,6 %) ont cette colonne vide.

**Valeurs manquantes** : aucune sur `Name`, `Brand`, `Description`,
`Image URL`. Seule `Notes` a des valeurs vides (80 lignes).

**Doublons** : aucun doublon exact ni quasi-doublon (nom + marque normalisés
casse/espaces/accents) détecté sur le dataset actuel (249 marques, toutes
distinctes après normalisation).

**Qualité** : au moins une ligne contient un caractère de remplacement (`�`)
issu d'une corruption dans le fichier source (ex. nom de parfum tronqué) —
nettoyé au notebook 02.

**Sortie du nettoyage** : `data/processed/nayaar_clean.csv` (encodage UTF-8),
colonnes brutes nettoyées + `notes_list` (liste de notes individuelles,
sérialisée en JSON dans la colonne CSV) + `notes_manquantes` (booléen).
Voir `data/notebooks/02_data_cleaning.ipynb` pour le détail du pipeline et le
rapport avant/après.

---

# Sources de référence (HORS pipeline — usage manuel uniquement)

Les sources ci-dessous ne sont JAMAIS lues par le code du MVP.
Elles servent uniquement au porteur du projet pour vérifier des
informations à la main et concevoir le modèle de données.
Aucun scraping n'est prévu.

## Source 2 — FragDB
Lien : https://huggingface.co/datasets/FragDBnet/fragrance-database
Usage : comprendre le schéma d'une base parfum professionnelle.
Version complète payante → non utilisée.

## Source 3 — Fragrantica
Lien : https://www.fragrantica.com/
Usage : vérification ponctuelle (familles, accords, pyramides).

## Source 4 — Parfumo
Lien : https://www.parfumo.com/
Usage : comparaison et validation manuelle.

## Source 5 — Basenotes
Lien : https://basenotes.com/
Usage : documentation, compréhension des notes.

---

# Source 6 — GPT (enrichissement, PAS source de vérité)

GPT n'est jamais une source de vérité.
Il intervient uniquement pour enrichir : générer certaines features,
proposer des classifications, produire des résumés.
Toute donnée produite par GPT est marquée comme probabiliste
et doit passer par une étape de validation avant intégration.

---

# Écart Kaggle → Knowledge Base (tableau d'origine des champs)

Ce tableau est la référence centrale du Feature Engineering.
Pour chaque champ de la Knowledge Base, il indique son origine et sa fiabilité.

| Champ                        | Origine                    | Fiabilité         |
|------------------------------|----------------------------|-------------------|
| id                           | Généré (index)             | ✅ Certain        |
| nom                          | Kaggle (direct)            | ✅ Certain        |
| marque                       | Kaggle (direct)            | ✅ Certain        |
| description                  | Kaggle (direct)            | ✅ Certain        |
| notes (brut)                 | Kaggle (direct)            | ✅ Certain        |
| image                        | Kaggle (direct)            | ✅ Certain        |
| concentration                | Dérivé du nom (regex)      | ⚠️ Partiel        |
| notes tête / cœur / fond     | Dérivé + IA                | ⚠️ Probabiliste   |
| famille / sous-famille       | IA (classification)        | ⚠️ Probabiliste   |
| accords                      | Dérivé des notes + IA      | ⚠️ Probabiliste   |
| projection / sillage / longévité | IA                     | ⚠️ Probabiliste   |
| scores saison                | IA                         | ⚠️ Probabiliste   |
| day / night score            | IA                         | ⚠️ Probabiliste   |
| scores style                 | IA                         | ⚠️ Probabiliste   |
| scores climat                | IA                         | ⚠️ Probabiliste   |
| scores usage                 | IA                         | ⚠️ Probabiliste   |
| compatible_perfumes          | Règles métier (layering)   | ⚠️ Heuristique    |
| compatibility_score          | Règles métier              | ⚠️ Heuristique    |
| generated_summary            | IA                         | ⚠️ Probabiliste   |
| keywords                     | Dérivé + IA                | ⚠️ Probabiliste   |
| embeddings                   | Généré (sentence-transf.)  | ✅ Déterministe   |

> Lecture : les champs ✅ sont fiables. Les champs ⚠️ doivent être
> considérés comme des estimations, validées par échantillonnage.

---

# Contenu de la Nayaar Knowledge Base

Chaque parfum possédera les champs regroupés ci-dessous.
(Se référer au tableau d'origine ci-dessus pour la fiabilité de chacun.)

## Identité
id · nom · marque · concentration

## Profil olfactif
famille · sous-famille · notes de tête · notes de cœur · notes de fond · accords

## Performances
projection · sillage · longévité

## Profil saisonnier
winter_score · spring_score · summer_score · autumn_score

## Moment
day_score · night_score

## Style
elegant · luxury · professional · romantic · mysterious · powerful · minimalist · creative

## Climat
hot_weather · cold_weather · humid_weather · dry_weather

## Usage
office · wedding · date · party · travel · business

## Layering
compatible_perfumes · compatibility_score

## IA
generated_summary · keywords · embeddings

---

# Embeddings

Générés à partir de plusieurs représentations textuelles :
description · notes · profil enrichi · résumé IA.
Ils alimentent le moteur RAG.

---

# Résultat

Le résultat final est une base de connaissances propriétaire :

# Nayaar Knowledge Base

C'est la source de vérité du projet.
Le chatbot, le moteur de recommandation, le moteur de layering et le RAG
travaillent EXCLUSIVEMENT sur cette base, jamais sur les données publiques.
