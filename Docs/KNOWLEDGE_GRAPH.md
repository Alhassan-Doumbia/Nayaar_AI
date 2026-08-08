# KNOWLEDGE GRAPH
# Nayaar – Structure du Knowledge Graph

Version : MVP v1.0 (implémenté)
Fichiers : `data/processed/nayaar_knowledge_base.csv`, `notes_vocabulary.json`,
`nayaar_index.faiss`, `nayaar_index_mapping.json`

---

# Principe

Le Nayaar Knowledge Graph est le véritable actif du projet — pas le chatbot.
Dans ce MVP, il n'est pas encore stocké dans un graphe formel (PostgreSQL +
pgvector, cible long terme) mais dans un ensemble de fichiers plats
équivalents fonctionnellement : chaque parfum y devient un ensemble structuré
de connaissances (famille, saison, moment, profil, texte de synthèse,
vecteur), exploitable par les moteurs de recommandation, de layering et de
RAG. Aucun utilisateur n'y accède directement.

---

# Composants du Knowledge Graph (MVP)

## 1. `nayaar_knowledge_base.csv`

Le cœur du Knowledge Graph. Une ligne par parfum (~2191), produite par le
pipeline décrit dans [FEATURE_ENGINEERING.md](FEATURE_ENGINEERING.md) :
données brutes (nom, marque, description, notes, image) enrichies des
features métier (famille, catégories de notes, scores saison/moment,
profil, concentration, texte de synthèse). Chargée une seule fois en mémoire
au démarrage du backend (`scoring.charger_knowledge_base`), réutilisée par
tous les moteurs — jamais rechargée à chaque requête.

## 2. `notes_vocabulary.json`

Le vocabulaire normalisé des notes olfactives : pour chaque note canonique,
sa catégorie parmi les 12 familles connues, ses scores heuristiques
(saisons, jour/nuit, profil) et un niveau de confiance. C'est le socle sur
lequel repose tout le feature engineering — toute normalisation de note côté
moteur (ex. préférences utilisateur) passe par ce mapping.

## 3. `nayaar_index.faiss` + `nayaar_index_mapping.json`

La couche vectorielle du Knowledge Graph : chaque `profil_text` est encodé
en un vecteur de 384 dimensions (`all-MiniLM-L6-v2`) et indexé dans un index
FAISS exact (`IndexFlatL2`). Le fichier de mapping associe chaque position
de l'index aux métadonnées du parfum correspondant (nom, marque, famille),
pour retrouver le parfum complet dans la Knowledge Base après une recherche
vectorielle.

---

# Comment le Knowledge Graph est interrogé

Aucun moteur ne modifie ces fichiers à l'exécution — ils sont en lecture
seule pour l'API, chargés une fois puis gardés en cache mémoire :

- Le **moteur de règles** parcourt la Knowledge Base et compare les
  préférences utilisateur aux features de chaque parfum.
- La **recherche sémantique** interroge l'index FAISS pour trouver les
  parfums dont le `profil_text` est le plus proche d'une requête libre.
- Le **moteur hybride** combine les deux pour le chat.
- Le **moteur de layering** parcourt la Knowledge Base pour comparer deux
  parfums entre eux (familles, catégories de notes, saison/moment, profil).
- Le **RAG** construit son contexte à partir des résultats de ces moteurs,
  jamais directement à partir des fichiers bruts.

---

# Évolution prévue

À terme (voir [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), section Évolution
Produit), ces fichiers plats seront remplacés par PostgreSQL + pgvector
(Supabase), ce qui permettra :

- des mises à jour incrémentales sans recharger l'intégralité du dataset ;
- l'ajout d'une table dédiée au layering (`Layer_ID`, `Perfume_A`,
  `Perfume_B`, `Compatibility_Score`, `Source`, `Validation_Status`,
  `Created_At`) alimentée progressivement par les retours utilisateurs ;
- le stockage de profils utilisateurs persistants et de leur historique de
  préférences, brique nécessaire à la véritable identité olfactive par
  client visée à long terme.

La structure logique des données (features par parfum, vecteurs, vocabulaire
de notes) reste la même — seul le support de stockage change.
