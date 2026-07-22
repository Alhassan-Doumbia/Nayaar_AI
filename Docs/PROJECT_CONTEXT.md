# PROJECT CONTEXT
# Nayaar – AI Powered Fragrance Intelligence Platform

Version : MVP v1.0
Author : Al Hassan Ahmed Doumbia
Project : Maison Nayaar

---

# 1. Vision

Nayaar est une future Maison de Parfumerie dont la différenciation repose sur une Intelligence Artificielle spécialisée dans la recommandation olfactive.

Contrairement aux assistants IA généralistes, Nayaar est conçu exclusivement pour comprendre l'univers de la parfumerie.

L'objectif n'est pas simplement de recommander un parfum mais de construire une véritable identité olfactive pour chaque client.

L'IA accompagne le client avant, pendant et après son achat.

A long terme, Nayaar deviendra un conseiller olfactif personnel disponible uniquement pour les clients de Maison Nayaar.

---

# 2. Objectifs du MVP

Le MVP poursuit quatre objectifs.

• Démontrer les capacités de l'IA dans la recommandation parfumée.

• Construire une première base de connaissances propriétaire.

• Répondre aux exigences techniques du Bootcamp IA.

• Poser les bases du futur produit commercial.

Le MVP ne cherche pas à construire une IA parfaite.

Il cherche à démontrer une architecture intelligente, évolutive et réaliste.

---

# 3. Philosophie

Nayaar n'utilise pas GPT comme moteur de décision.

Le moteur de décision repose sur :

- les données
- le feature engineering
- le moteur de scoring
- les règles métier

GPT intervient uniquement pour :

- comprendre les demandes
- reformuler
- expliquer
- dialoguer naturellement

Cette séparation est volontaire afin d'améliorer l'explicabilité des recommandations.

---

# 4. Les deux grands composants du projet

Le projet est composé de deux systèmes.

## A. Nayaar Knowledge Graph

Le cerveau.

Il contient toutes les connaissances métier.

Il est responsable de :

- l'import des données
- le nettoyage
- le feature engineering
- les embeddings
- les recommandations
- le RAG

Aucun utilisateur n'interagit directement avec lui.

---

## B. Nayaar Assistant

Le visage.

Il s'agit du chatbot.

Le chatbot dialogue avec le client.

Il interroge le Knowledge Graph.

Puis il reformule les résultats de manière naturelle.

---

# 5. Architecture globale

                User

                  │

            NextJS Frontend

                  │

              Python API

                  │

     ┌────────────┼────────────┐

     │            │            │

Recommendation   RAG       GPT Chat

     │            │

     └────────────┼────────────┘

                  │

        Nayaar Knowledge Graph

                  │

        PostgreSQL + pgvector

---

# 6. Stack Technique

Frontend

- Next.js

Backend

- Python

Framework API

- FastAPI

Base de données

- PostgreSQL (Supabase)

Embeddings

- pgvector

LLM

- GPT

Data Science

- Pandas
- NumPy
- Scikit Learn

NLP

- spaCy
- sentence-transformers

Visualisation

- Matplotlib
- Seaborn

---

# 7. Source des données

Le dataset principal provient du Kaggle Perfume Recommendation Dataset (~2191 parfums).

Ces données représentent uniquement la vérité de référence.

Elles ne seront jamais modifiées.

# 8. Pipeline Data Analysis et Feature Engineering

La construction du Nayaar Knowledge Graph commence par une phase complète d'analyse et de préparation des données.

Cette étape doit être réalisée dans un ou plusieurs notebooks Jupyter Notebook (.ipynb).

Les notebooks constituent la documentation analytique du projet et doivent permettre de comprendre :

- la structure initiale du dataset Kaggle ;
- la qualité des données ;
- les transformations appliquées ;
- la création des nouvelles features utilisées par l'intelligence artificielle.

---

# 8.1 Organisation des notebooks

Les notebooks doivent être séparés selon les responsabilités.

Exemple :

notebooks/

│

├── 01_data_exploration.ipynb

Analyse exploratoire du dataset brut.

Objectifs :

- Chargement des données Kaggle.
- Présentation des différentes colonnes.
- Analyse du nombre de parfums.
- Analyse des marques présentes.
- Analyse des valeurs manquantes.
- Analyse des doublons.
- Statistiques générales.

---

├── 02_data_cleaning.ipynb

Nettoyage et préparation des données.

Objectifs :

- Suppression des doublons.
- Gestion des valeurs manquantes.
- Normalisation des formats.
- Harmonisation des catégories.
- Préparation des textes pour le NLP.

---

├── 03_feature_engineering.ipynb

Création du dataset enrichi Nayaar.

Objectifs :

Transformer les données brutes de parfumerie en données exploitables par le moteur IA.

Création de nouvelles caractéristiques :

- familles olfactives enrichies ;
- sous-familles ;
- profils saisonniers ;
- profils émotionnels ;
- styles ;
- occasions ;
- contexte d'utilisation ;
- scores de compatibilité.

---

├── 04_embeddings_preparation.ipynb

Préparation des données pour la recherche sémantique.

Objectifs :

- Création des textes enrichis.
- Génération des embeddings.
- Préparation pour stockage dans PostgreSQL + pgvector ou FAISS.
- Vérification de la qualité des représentations vectorielles.

---

# 8.2 Visualisation des données

Les notebooks doivent contenir des visualisations permettant de comprendre le dataset.

Bibliothèques utilisées :

- Matplotlib
- Seaborn
- Pandas Visualization

Les visualisations exactes seront définies ultérieurement.

Exemples de visualisations possibles :

## Distribution des familles olfactives

Objectif :

Comprendre la répartition des profils parfumés présents dans le dataset.


## Analyse des marques

Objectif :

Identifier les maisons les plus représentées.


## Analyse des notes

Objectif :

Identifier les notes dominantes dans la base.


## Analyse des accords

Objectif :

Comprendre les tendances olfactives.


## Corrélations entre features

Objectif :

Identifier les relations entre :

- notes ;
- familles ;
- saisons ;
- styles ;
- occasions.


## Visualisation après Feature Engineering

Objectif :

Montrer comment les données brutes deviennent des profils exploitables par Nayaar.


---

# 8.3 Principes Data Science

Les notebooks doivent respecter les bonnes pratiques :

- Code Python propre et commenté.
- Fonctions réutilisables.
- Variables explicites.
- Étapes clairement séparées.
- Résultats reproductibles.

Le notebook doit raconter une histoire :

Dataset brut

↓

Compréhension des données

↓

Nettoyage

↓

Transformation

↓

Feature Engineering

↓

Knowledge Graph Nayaar

---

# 8.4 Résultat attendu

À la fin de cette étape, le projet doit disposer d'un dataset Nayaar enrichi contenant :

- les données originales du dataset Kaggle ;
- les nouvelles features métier ;
- les informations nécessaires au moteur de recommandation ;
- les textes enrichis nécessaires au RAG ;
- les données prêtes pour la génération d'embeddings.

Ce dataset enrichi devient la première version du Nayaar Knowledge Graph.


# 9. Niveau 1 : Raw Dataset

Chaque parfum possède des informations comme :

- nom
- marque
- concentration
- description
- notes
- famille
- sous-famille

Ces données sont importées puis stockées.

Elles sont immuables.

---

# 10. Niveau 2 : Feature Engineering

Le Feature Engineering constitue le cœur de Nayaar.

L'objectif est de transformer les informations parfumées en connaissances exploitables.

Les nouvelles colonnes seront générées automatiquement.

Exemples :

## Saison

Winter Score

Summer Score

Spring Score

Autumn Score

---

## Moment

Day Score

Night Score

---

## Style

Luxury

Elegant

Professional

Romantic

Creative

Minimalist

Powerful

Mysterious

Fresh

Warm

Comforting

---

## Usage

Office

Wedding

Party

Date

Business Meeting

Mosque

Travel

Vacation

---

## Performance

Projection Score

Sillage Score

Longevity Score

---

## Profil

Masculine

Feminine

Unisex

---

## Climat

Cold Weather

Hot Weather

Humid Weather

Dry Weather

---

Toutes ces colonnes sont produites par une IA d'enrichissement.

Le résultat est validé puis stocké.

GPT n'intervient plus ensuite.

---

# 11. Layering Engine

Le Layering constitue l'une des principales innovations de Nayaar.

Le MVP fonctionne selon des règles métier.

Le moteur compare :

- familles
- sous-familles
- accords
- notes

Puis calcule un score de compatibilité.

Plus tard, les recommandations des utilisateurs alimenteront progressivement le système.

Une table dédiée sera créée.

Layer_ID

Perfume_A

Perfume_B

Compatibility_Score

Source

Validation_Status

Created_At

---

# 12. Recommendation Engine

Le MVP repose principalement sur un moteur de scoring.

Le score final est calculé à partir de :

Familles

+

Notes

+

Saison

+

Moment

+

Style

+

Usage

+

Climat

+

Budget

+

Préférences utilisateur

Le Collaborative Filtering (KNN) sera ajouté lorsque suffisamment de données utilisateurs seront disponibles.

---

# 13. Knowledge Graph

Le Knowledge Graph constitue le véritable actif du projet.

Chaque parfum devient un ensemble de connaissances.

Exemple :

Dior Homme Intense

↓

Elegant

Luxury

Office

Winter

Formal

Night

Business

↓

Embeddings

↓

Recherche

↓

Réponse

---

# 14. Embeddings

Chaque parfum possède plusieurs embeddings.

Description

Notes

Profil enrichi

Layerings

Ces embeddings servent au RAG.

---

# 15. RAG

Le pipeline est :

Question utilisateur

↓

Embedding

↓

Recherche Vectorielle

↓

Contexte

↓

GPT

↓

Réponse

Le LLM ne répond jamais sans contexte.

---

# 16. GPT

Le LLM possède quatre rôles.

Comprendre.

Expliquer.

Conseiller.

Converser.

Il ne décide jamais seul.

---

# 17. Application Nayaar

Le MVP comporte une interface simple.

Fonctionnalités :

Chat

Recherche de parfum

Recherche par intention

Conseil personnalisé

Suggestion de layering

Explication des recommandations

---

# 18. Evolution Produit

Version 1

Dataset enrichi

↓

Version 2

Knowledge Graph

↓

Version 3

Application Mobile

↓

Version 4

Profils utilisateurs

↓

Version 5

Collaborative Filtering

↓

Version 6

Apprentissage communautaire

↓

Version 7

Assistant IA Premium

---

# 19. Vision Long Terme

Le véritable produit de Nayaar n'est pas le chatbot.

Le véritable produit est le Knowledge Graph.

Le chatbot n'est qu'une interface permettant aux utilisateurs d'interagir avec cette intelligence.

Plus les utilisateurs utiliseront Nayaar, plus la base de connaissances s'enrichira.

L'objectif est de créer le premier conseiller olfactif intelligent spécialisé capable de construire, comprendre et faire évoluer le profil olfactif de chaque client.

Le véritable avantage concurrentiel de Nayaar ne repose pas sur GPT.

Il repose sur la qualité de son Knowledge Graph, son Feature Engineering et les données accumulées au fil du temps.