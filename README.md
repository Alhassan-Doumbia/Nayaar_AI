# Nayaar — AI Powered Fragrance Intelligence Platform

## Pertinence et objectif du projet

Le marché du parfum est aujourd'hui dominé par des recommandations génériques :
filtres par famille olfactive, best-sellers, ou avis clients peu personnalisés.
Aucun acteur ne construit une véritable compréhension du profil olfactif de
chaque client dans la durée.

Nayaar part d'un constat simple : choisir un parfum est une décision intime et
complexe (occasion, saison, style, budget, notes déjà aimées ou rejetées), que
les outils existants ne traitent pas correctement. L'objectif du projet n'est
donc pas de construire "un chatbot qui recommande des parfums", mais de poser
les bases d'une véritable **identité olfactive par client** : un système
capable de comprendre, structurer et faire évoluer les préférences d'un
utilisateur avant, pendant et après son achat.

Ce dépôt contient le MVP de cette vision : un moteur de recommandation basé
sur des données et des règles métier explicables, un moteur de compatibilité
entre parfums (layering), et une interface conversationnelle qui reformule ces
résultats en langage naturel — sans jamais laisser le langage naturel décider
à la place des données.

Ce MVP a été réalisé dans le cadre d'un Bootcamp IA / Data Science, et sert
également de socle technique pour le futur produit commercial de la Maison
Nayaar.

## Principe fondateur

**L'IA générative n'est jamais le moteur de décision.**

Le moteur de décision est composé de données, de feature engineering, d'un
moteur de scoring et de règles métier explicites. Le LLM (Claude) n'intervient
qu'après coup, pour comprendre une demande, expliquer un résultat déjà calculé,
ou dialoguer naturellement avec l'utilisateur. Cette séparation stricte est
volontaire : elle garantit que chaque recommandation reste explicable et
traçable jusqu'aux données qui l'ont produite, plutôt que de dépendre du
jugement opaque d'un modèle de langage.

## Les deux composants du projet

- **Nayaar Knowledge Graph** (le cerveau) — import et nettoyage des données,
  feature engineering, embeddings, moteur de recommandation, moteur de
  layering, pipeline RAG. Aucun utilisateur final n'y accède directement ;
  c'est le véritable actif du projet.
- **Nayaar Assistant** (le visage) — l'application web qui interroge le
  Knowledge Graph et reformule ses résultats de façon naturelle pour
  l'utilisateur.

## Fonctionnalités du MVP

- Recommandation de parfums par moteur de scoring (familles, notes, saison,
  moment, style, usage, climat, budget, préférences utilisateur).
- Recherche sémantique par description libre (embeddings + FAISS).
- Recherche de parfums par nom, tolérante aux fautes de frappe.
- Moteur de layering : calcule un score de compatibilité entre deux parfums à
  partir de règles métier (familles, sous-familles, accords, notes).
- Assistant conversationnel (mode consultation autonome, sans historique) qui
  explique et reformule les résultats des moteurs ci-dessus, sans jamais
  générer de recommandation par lui-même.

## Stack technique

| Couche | Technologie |
|---|---|
| Frontend | Next.js (JavaScript, pas de TypeScript) |
| Backend API | Python / FastAPI |
| Base de données (cible) | PostgreSQL (Supabase) + pgvector |
| Recherche vectorielle (MVP) | FAISS |
| LLM | Claude (Anthropic) — rôle : comprendre / expliquer / conseiller / converser, jamais décider |
| Data Science | Pandas, NumPy, Scikit-Learn |
| NLP | spaCy, sentence-transformers |
| Visualisation | Matplotlib, Seaborn |

Détails complets : [Docs/TECH_STACK.md](Docs/TECH_STACK.md).

## Source des données

Le dataset de référence provient d'un jeu de données Kaggle d'environ 2191
parfums. Ces données brutes constituent la vérité de référence du projet et
sont immuables : toute transformation ou enrichissement crée de nouvelles
colonnes ou tables, sans jamais écraser les données sources.

## Structure du dépôt

```
.
├── CLAUDE.md                  Point d'entrée pour le développement assisté par IA
├── Docs/                      Documentation détaillée (vision, schéma DB, moteurs, RAG, roadmap)
├── data/
│   └── notebooks/             Notebooks de data science (exploration, nettoyage,
│                               feature engineering, embeddings)
├── backend/
│   └── app/
│       ├── main.py            Point d'entrée de l'API FastAPI
│       ├── recommendation/    Moteurs de scoring, recherche sémantique, hybride, layering
│       ├── chat/               Pipeline RAG et prompts système Claude
│       └── routes/            Endpoints REST exposés au frontend
└── frontend/
    └── app/                   Application Next.js (chat, layering, recherche)
```

## Démarrage rapide

### Backend

```
cd backend/app
python main.py
```

Lance l'API FastAPI sur `0.0.0.0:8000` (accessible depuis le réseau local,
pratique pour une démonstration sur un autre appareil que l'ordinateur de
développement).

### Frontend

```
cd frontend
npm run dev
```

L'IP réseau locale utilisée pour joindre le backend est détectée et
configurée automatiquement avant chaque lancement (voir
`frontend/scripts/update-network-ip.js`), ce qui permet de faire une
démonstration sur n'importe quel réseau Wi-Fi sans configuration manuelle.

## Documentation complémentaire

Le détail de la vision produit, de la roadmap, du schéma de base de données,
du feature engineering, des moteurs de recommandation et de layering, et du
pipeline RAG est disponible dans le dossier [Docs/](Docs/), en particulier
[Docs/PROJECT_CONTEXT.md](Docs/PROJECT_CONTEXT.md).
