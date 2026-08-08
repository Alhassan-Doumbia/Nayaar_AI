# FEATURE ENGINEERING
# Nayaar – Enrichissement des données

Version : MVP v1.0 (implémenté)
Notebooks : `data/notebooks/02_data_cleaning.ipynb`, `03a_notes_vocabulary.ipynb`,
`03b_feature_engineering.ipynb`, `03c_features_validation.ipynb`

---

# Principe

Toutes les features métier sont produites par des **règles explicites**,
jamais par un appel à un LLM — condition nécessaire à l'explicabilité du
moteur de scoring. Le pipeline suit une progression stricte : nettoyage,
vocabulaire, feature engineering, validation manuelle.

---

# 1. `02_data_cleaning` — Nettoyage

Nettoie le dataset brut Kaggle (`data/raw/final_perfume_data.csv.zip`,
~2191 parfums), sans feature engineering :

- Suppression des doublons (clé nom + marque normalisée).
- Gestion des valeurs manquantes, documentée colonne par colonne (ex. une
  note manquante est conservée mais marquée `notes_manquantes = True` plutôt
  que supprimée ou inventée).
- Normalisation des textes et des marques.
- Parsing du champ `Notes` en une liste plate (`notes_list`), sans structure
  tête/cœur/fond à ce stade.

Sortie : `nayaar_clean.csv`.

---

# 2. `03a_notes_vocabulary` — Vocabulaire de notes

Construit le vocabulaire normalisé des notes à partir de `notes_list` :

- Normalisation des variantes d'écriture d'une même note (mapping explicite).
- Catégorisation de chaque note dans l'une des 12 familles olfactives
  connues (les notes non catégorisées automatiquement sont listées pour un
  traitement manuel).
- Attribution d'attributs métier heuristiques par note (saison, moment,
  profil), à partir d'une base de scores par catégorie ajustée par
  mots-clés. Chaque entrée est marquée `attributs_heuristiques: true` —
  pensée pour être relue et corrigée à la main.

Sortie : `notes_vocabulary.json`.

---

# 3. `03b_feature_engineering` — Construction de la Knowledge Base

Combine `nayaar_clean.csv` et `notes_vocabulary.json` pour produire la
Nayaar Knowledge Base, entièrement par règles (aucun appel GPT).

## Features créées

| Feature | Description |
|---|---|
| `notes_categories` | Ensemble des catégories olfactives présentes dans les notes reconnues, triées par fréquence décroissante |
| `famille` | Catégorie olfactive dominante (comptage des notes reconnues par catégorie), avec un ordre de départage explicite en cas d'égalité |
| `winter_score`, `spring_score`, `summer_score`, `autumn_score` | Moyenne des scores heuristiques des notes reconnues pour chaque saison ; 0.5 (neutre) par défaut si aucune note reconnue |
| `day_score`, `night_score` | Même principe pour le moment de la journée |
| `profil` | masculine / feminine / unisex — priorité aux mots-clés explicites du nom/description, sinon moyenne des tendances de profil des notes reconnues |
| `concentration` | Extraite par expressions régulières sur le nom (Extrait de Parfum, Eau de Parfum, Eau de Toilette, Cologne Absolue, Eau de Cologne, Eau Fraiche, Elixir, Perfume Oil, Attar, Absolu, Parfum, Cologne — du plus spécifique au plus générique) |
| `profil_text` | Texte de synthèse en langage naturel (nom, marque, famille, notes reconnues, attributs), utilisé ensuite pour générer les embeddings |

Il n'existe pas dans ce MVP de features distinctes « style », « usage »,
« performance » ou « climat » — volontairement reportées (voir
[MVP_SCOPE.md](MVP_SCOPE.md)) faute de données fiables pour les produire à
ce stade.

Sortie : `nayaar_knowledge_base.csv` (colonnes : `Name`, `Brand`,
`Description`, `Notes`, `Image URL`, `notes_manquantes`, `notes_list`,
`notes_categories`, `famille`, les 6 scores saison/moment, `profil`,
`concentration`, `profil_text`).

---

# 4. `03c_features_validation` — Validation

Contrôle qualité manuel du dataset enrichi, sans aucune correction
automatique à ce stade — uniquement affichage et tests :

- Échantillon de 30 parfums inspecté manuellement.
- Tests automatiques : tous les scores dans `[0, 1]`, valeur neutre par
  défaut correctement appliquée en l'absence de notes reconnues, familles et
  profils et concentrations valides, cohérence intuitive été/hiver sur des
  cas connus, taux de remplissage par colonne.
- Visualisations (Matplotlib / Seaborn) de la distribution des familles,
  des marques et des scores saisonniers.

---

# Résultat

À l'issue de ce pipeline, `nayaar_knowledge_base.csv` et
`notes_vocabulary.json` constituent la première version de la Nayaar
Knowledge Base — la seule source que les moteurs de recommandation, de
layering et de RAG interrogent ensuite. Voir
[KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md).
