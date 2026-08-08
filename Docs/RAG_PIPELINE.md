# RAG PIPELINE
# Nayaar – Pipeline de retrieval-augmented generation

Version : MVP v1.0 (implémenté)
Fichiers : `backend/app/chat/rag.py`, `backend/app/chat/system_prompt.py`
Route : `POST /api/chat`

---

# Principe

Claude ne répond jamais à partir de sa seule connaissance générale du parfum.
Chaque réponse doit s'appuyer sur un contexte construit à partir des
résultats réels du moteur de recommandation. C'est la règle métier
« RAG obligatoire pour les réponses factuelles » : le LLM comprend, reformule
et explique, il ne recherche ni ne décide jamais seul.

---

# Étapes du pipeline

1. **Requête** : `POST /api/chat` reçoit un message utilisateur en langage
   libre (et un `session_id` optionnel, généré automatiquement s'il est
   absent — utilisé uniquement pour du regroupement côté frontend, sans
   influence sur la réponse).

2. **Recherche hybride** : le message est passé au moteur hybride
   (`hybrid.recherche_hybride`), qui combine recherche sémantique (embedding
   de la question comparé à l'index FAISS) et re-classement par le moteur de
   règles (notes, famille, saison, moment, profil). Voir
   [RECOMMENDATION_ENGINE.md](RECOMMENDATION_ENGINE.md).

3. **Filtrage de pertinence** : les résultats dont le score hybride est
   inférieur à un seuil minimum (0.3) sont écartés, pour éviter de forcer
   Claude à commenter des parfums hors sujet.

4. **Construction du contexte** : les résultats retenus sont transformés en
   un texte structuré listant, pour chaque parfum classé, son nom, sa
   marque, sa famille, son score global et le détail de chaque contribution.
   S'il ne reste aucun résultat pertinent, le contexte l'indique
   explicitement (« Aucun résultat pertinent trouvé »).

5. **Appel à Claude** : le contexte et la question sont envoyés à l'API
   Claude (modèle `claude-haiku-4-5-20251001`) avec le système prompt dédié
   (`system_prompt.py`).

6. **Réponse** : le texte de Claude et les résultats bruts filtrés sont
   renvoyés au frontend, qui les affiche sous forme de bulle de chat et de
   cartes parfum.

---

# Ce que le système prompt impose à Claude

- Répondre uniquement à partir des parfums présents dans le contexte, sans
  jamais en inventer.
- Ne jamais modifier l'ordre de classement produit par le moteur.
- Justifier chaque recommandation par les contributions réelles du score
  (notes, famille, saison, moment, profil, proximité sémantique), sans
  inventer d'autre justification.
- Dire honnêtement qu'aucun résultat pertinent n'a été trouvé si le contexte
  l'indique, plutôt que de combler ce vide par une réponse générique.
- Ton chaleureux de conseiller olfactif, toujours en français, concis, sans
  jargon technique brut, sans emoji.

---

# Mode « consultation autonome »

Le pipeline est volontairement **sans état** : `rag.repondre()` ne prend en
entrée que la question courante, aucun historique de conversation n'est
stocké ni transmis à Claude. Chaque appel est une consultation complète en
elle-même — recommandation et justification dès la première réponse, sans
question de relance.

Conséquence assumée : un message de suivi du type « pourquoi ce choix ? »
est traité par le moteur hybride comme une toute nouvelle recherche
indépendante, sans lien avec l'échange précédent. Ce choix est délibéré :
il garantit que la réponse reste toujours explicable et reproductible à
partir du seul message reçu, sans dépendre d'un historique susceptible de
dériver ou d'introduire un biais non contrôlé par le moteur de scoring.

---

# Le pipeline de layering suit le même principe

`POST /api/layering` applique exactement la même logique (contexte construit
à partir d'un résultat de moteur, système prompt dédié, réponse en un seul
tour sans historique) — voir [LAYERING_ENGINE.md](LAYERING_ENGINE.md).
