# DATABASE SCHEMA
# Nayaar – Schéma de données

Version : MVP v1.0 (stockage fichiers) → cible PostgreSQL + pgvector

---

# Principe

Le MVP ne déploie pas encore de base de données : la Knowledge Base vit dans
des fichiers plats sous `data/processed/`, chargés une seule fois en mémoire
au démarrage du backend. Cette section documente d'abord ce schéma réel tel
qu'implémenté, puis le schéma PostgreSQL cible vers lequel il migrera (voir
[KNOWLEDGE_GRAPH.md](KNOWLEDGE_GRAPH.md), section Évolution prévue).

---

# 1. Schéma actuel (MVP) — `nayaar_knowledge_base.csv`

Une ligne par parfum (~2191). L'index de la ligne dans le fichier fait
office d'identifiant (`id`) utilisé par `GET /api/perfumes/{id}` et par
l'index FAISS — les deux doivent rester dans le même ordre.

| Colonne | Type | Description |
|---|---|---|
| `Name` | texte | Nom du parfum |
| `Brand` | texte | Marque |
| `Description` | texte | Description libre (source Kaggle) |
| `Notes` | texte | Notes olfactives brutes, telles que fournies par le dataset source |
| `Image URL` | texte | URL de l'image du produit |
| `notes_manquantes` | booléen | `True` si aucune note n'a pu être extraite pour ce parfum |
| `notes_list` | liste JSON | Notes brutes parsées en liste plate |
| `notes_categories` | liste JSON | Catégories olfactives (parmi 12) présentes dans les notes reconnues, triées par fréquence |
| `famille` | texte | Famille olfactive dominante |
| `winter_score`, `spring_score`, `summer_score`, `autumn_score` | flottant `[0,1]` | Scores saisonniers |
| `day_score`, `night_score` | flottant `[0,1]` | Scores de moment |
| `profil` | texte | `masculine` / `feminine` / `unisex` |
| `concentration` | texte | Concentration extraite du nom (Eau de Parfum, Eau de Toilette...), vide si non détectée |
| `profil_text` | texte | Texte de synthèse utilisé pour générer l'embedding |

Les données brutes Kaggle (`Name`, `Brand`, `Description`, `Notes`,
`Image URL`) sont immuables : toute colonne ajoutée par le pipeline
d'enrichissement est une nouvelle colonne, jamais un écrasement.

## `notes_vocabulary.json`

Dictionnaire indexé par note canonique :

```
{
  "<note>": {
    "categorie": "<une des 12 familles>",
    "winter_score": 0.0-1.0, "spring_score": ..., "summer_score": ..., "autumn_score": ...,
    "day_score": 0.0-1.0, "night_score": ...,
    "profil": "masculine|feminine|unisex",
    "attributs_heuristiques": true,
    "confiance": "..."
  }
}
```

## `nayaar_index.faiss` + `nayaar_index_mapping.json`

Index vectoriel FAISS (`IndexFlatL2`, 384 dimensions) construit sur
`profil_text`. Le mapping JSON associe chaque position de l'index à
`{nom, marque, famille}`, dans le même ordre que la Knowledge Base.

---

# 2. Schéma cible — PostgreSQL (Supabase) + pgvector

Le schéma ci-dessous formalise le passage à une base relationnelle, sans
changer la structure logique des données.

## Table `perfumes`

| Colonne | Type | Description |
|---|---|---|
| `id` | `serial primary key` | Identifiant stable du parfum |
| `name` | `text` | Nom (immuable, source Kaggle) |
| `brand` | `text` | Marque (immuable, source Kaggle) |
| `description` | `text` | Description (immuable, source Kaggle) |
| `notes_raw` | `text` | Notes brutes (immuable, source Kaggle) |
| `image_url` | `text` | URL de l'image |
| `created_at` | `timestamptz` | Date d'import |

## Table `perfume_features` (1-1 avec `perfumes`, enrichissement)

| Colonne | Type | Description |
|---|---|---|
| `perfume_id` | `int references perfumes(id)` | |
| `notes_list` | `text[]` | Notes parsées |
| `notes_categories` | `text[]` | Catégories olfactives présentes |
| `famille` | `text` | Famille dominante |
| `winter_score`, `spring_score`, `summer_score`, `autumn_score` | `float` | Scores saisonniers |
| `day_score`, `night_score` | `float` | Scores de moment |
| `profil` | `text` | masculine / feminine / unisex |
| `concentration` | `text` | Concentration détectée |
| `profil_text` | `text` | Texte de synthèse (source de l'embedding) |
| `embedding` | `vector(384)` | Embedding pgvector, remplace l'index FAISS |

## Table `notes_vocabulary`

| Colonne | Type | Description |
|---|---|---|
| `note` | `text primary key` | Note canonique |
| `categorie` | `text` | Une des 12 familles olfactives |
| `winter_score` ... `night_score` | `float` | Scores heuristiques |
| `profil` | `text` | Tendance de profil |
| `confiance` | `text` | Niveau de confiance de l'heuristique |

## Table `layerings` (voir [LAYERING_ENGINE.md](LAYERING_ENGINE.md))

| Colonne | Type | Description |
|---|---|---|
| `layer_id` | `serial primary key` | |
| `perfume_a` | `int references perfumes(id)` | |
| `perfume_b` | `int references perfumes(id)` | |
| `compatibility_score` | `float` | Score calculé par le moteur de layering |
| `source` | `text` | `engine` (calculé) ou `user` (retour utilisateur, hors MVP) |
| `validation_status` | `text` | Statut de validation |
| `created_at` | `timestamptz` | |

## Tables futures (hors MVP, voir [MVP_SCOPE.md](MVP_SCOPE.md))

- `users` : profils clients persistants.
- `user_preferences` : historique des préférences et interactions, base de
  la future identité olfactive par client et du Collaborative Filtering.

---

# Règle de migration

Le passage du CSV/FAISS à PostgreSQL/pgvector ne doit modifier ni les noms
de features ni leur mode de calcul (toujours des règles explicites) — seul
le support de stockage change, pour ne jamais remettre en cause
l'explicabilité déjà validée du moteur.
