# Nayaar — AI Powered Fragrance Intelligence Platform

Point d'entrée pour toute intervention de Claude sur ce repo. Lire ce fichier en premier,
puis se référer aux docs détaillés dans `Docs/` selon le sujet traité.

## Vision (résumé)

Nayaar est une future Maison de Parfumerie dont la différenciation repose sur une IA
spécialisée dans la recommandation olfactive — pas un chatbot généraliste. L'objectif
n'est pas de recommander un parfum mais de construire une véritable **identité olfactive**
par client, avant/pendant/après l'achat.

**Philosophie clé : GPT n'est jamais le moteur de décision.**
Le moteur de décision = données + feature engineering + scoring + règles métier.
GPT sert uniquement à comprendre, reformuler, expliquer, dialoguer. Cette séparation est
volontaire pour préserver l'explicabilité des recommandations. Ne jamais laisser GPT
décider seul d'une recommandation ou générer une feature métier sans passage par le
pipeline de scoring/règles.

## Les deux composants

- **Nayaar Knowledge Graph** (le cerveau) — import, nettoyage, feature engineering,
  embeddings, recommandations, RAG. Aucun utilisateur n'y accède directement.
- **Nayaar Assistant** (le visage) — chatbot Next.js qui interroge le Knowledge Graph
  et reformule les résultats en langage naturel.

Le vrai actif du projet est le **Knowledge Graph**, pas le chatbot.

## Stack technique

| Couche | Techno |
|---|---|
| Frontend | Next.js (JavaScript, **pas de TypeScript**) |
| Backend API | Python / FastAPI |
| Base de données | PostgreSQL (Supabase) |
| Vecteurs | pgvector |
| LLM | GPT (rôle : comprendre / expliquer / conseiller / converser, jamais décider) |
| Data Science | Pandas, NumPy, Scikit-Learn |
| NLP | spaCy, sentence-transformers |
| Visualisation | Matplotlib, Seaborn |

Détails complets : [Docs/TECH_STACK.md](Docs/TECH_STACK.md)

## Conventions de code

- **Python** : niveau intermédiaire, code commenté **en français**, fonctions
  réutilisables, variables explicites, étapes clairement séparées. Notebooks (`.ipynb`)
  organisés par responsabilité (exploration, cleaning, feature engineering, embeddings)
  et doivent raconter une histoire reproductible : brut → compréhension → nettoyage →
  transformation → feature engineering → Knowledge Graph.
- **Frontend** : React / Next.js en **JavaScript pur, sans TypeScript**.
- Pas d'abstraction prématurée, pas de sur-ingénierie : coller au besoin réel du MVP.
- Les données brutes du dataset Kaggle (~2191 parfums) sont la **vérité de référence
  et sont immuables** — toute transformation crée de nouvelles colonnes/tables, jamais
  d'écrasement des données sources.

## Règles métier absolues

1. **GPT ne décide jamais seul.** Toute recommandation passe par le moteur de scoring
   (familles + notes + saison + moment + style + usage + climat + budget + préférences).
2. **Séparation stricte données/LLM.** Le feature engineering (saison, style, usage,
   performance, profil, climat, etc.) est produit par un pipeline IA validé puis stocké
   — GPT n'intervient plus après validation.
3. **RAG obligatoire pour les réponses factuelles.** Le LLM ne répond jamais sans
   contexte issu de la recherche vectorielle sur le Knowledge Graph.
4. **Dataset source immuable.** Ne jamais modifier les données brutes Kaggle ; toujours
   enrichir via de nouvelles colonnes/tables dédiées.
5. **Layering Engine basé règles métier** (comparaison familles/sous-familles/accords/
   notes → score de compatibilité), pas de ML "boîte noire" tant que les données
   utilisateurs sont insuffisantes.

## Arborescence du repo

```
.
├── CLAUDE.md                  # ce fichier — point d'entrée
├── Docs/                      # documentation détaillée par sujet
│   ├── PROJECT_CONTEXT.md     # vision, architecture, roadmap complets
│   ├── TECH_STACK.md          # détails stack technique
│   ├── DATABASE_SCHEMA.md     # schéma PostgreSQL / pgvector
│   ├── FEATURE_ENGINEERING.md # spec des features métier (saison, style, usage...)
│   ├── KNOWLEDGE_GRAPH.md     # structure du Knowledge Graph
│   ├── LAYERING_ENGINE.md     # règles de compatibilité entre parfums
│   ├── RECOMMENDATION_ENGINE.md # moteur de scoring
│   ├── RAG_PIPELINE.md        # pipeline retrieval-augmented generation
│   ├── GPT_SYSTEM_PROMPT.md   # prompt système du LLM (rôles autorisés)
│   └── ROADMAP.md             # évolution produit (v1 → v7)
├── Prompts/                   # prompts de travail
├── notebooks/                 # (à créer) 01_data_exploration, 02_data_cleaning,
│                               #   03_feature_engineering, 04_embeddings_preparation
└── ... (frontend Next.js, backend FastAPI — à créer)
```

> Plusieurs fichiers dans `Docs/` sont pour l'instant vides (placeholders) sauf
> `PROJECT_CONTEXT.md`. Les compléter au fur et à mesure du projet plutôt que de
> dupliquer leur contenu ici.

## Comment utiliser ce fichier

- Pour une question de vision/roadmap produit → `Docs/PROJECT_CONTEXT.md`.
- Pour une question de schéma DB / features / scoring / RAG / layering → le fichier
  `Docs/` correspondant (à compléter si vide).
- Pour toute génération de code : respecter les conventions ci-dessus (Python commenté
  en français, JS sans TypeScript côté front) et ne jamais violer les règles métier
  absolues, en particulier la séparation données/scoring vs GPT.
