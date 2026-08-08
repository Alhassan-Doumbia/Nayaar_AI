# LAYERING ENGINE
# Nayaar – Moteur de compatibilité pour le layering

Version : MVP v1.0 (implémenté)
Fichiers : `backend/app/recommendation/layering.py`, `backend/app/chat/layering_rag.py`,
`backend/app/chat/layering_system_prompt.py`
Route : `POST /api/layering`

---

# Principe

Le layering consiste à superposer deux parfums (une base et un dessus) pour
créer une signature olfactive unique. Comme pour la recommandation, le score
de compatibilité entre deux parfums est calculé **exclusivement par des
règles métier**, jamais par un LLM. Claude n'intervient qu'ensuite, pour
reformuler le résultat déjà calculé en guide d'application.

---

# 1. Calcul du score de compatibilité

Le score combine 4 composantes pondérées (somme = 1.0) :

| Composante | Poids | Ce qu'elle mesure |
|---|---|---|
| Catégories | 0.35 | Compatibilité entre familles olfactives dominantes |
| Complémentarité | 0.25 | Diversité des catégories de notes apportées par le candidat |
| Saison / moment | 0.25 | Cohérence des profils saisonniers et jour/nuit |
| Profil | 0.15 | Cohérence des profils (masculin / féminin / unisexe) |

## Détail de chaque composante

- **Catégories** : une matrice de compatibilité, indexée par paire de
  familles, donne un score explicite pour chaque combinaison (de 0.20 pour
  des associations qui se neutralisent, ex. aquatique + gourmand, à 0.90
  pour des mariages classiques, ex. gourmand + boisé, floral + musqué,
  ambré + épicé). Deux parfums de même famille obtiennent 0.55 (cohérents
  mais peu complémentaires). Une paire absente de la matrice obtient un
  score neutre de 0.55.
- **Complémentarité** : proportion des catégories de notes du candidat qui
  sont absentes chez le parfum de référence — récompense la diversité,
  pénalise la redondance totale.
- **Saison / moment** : moyenne de la cohérence sur les 4 scores saisonniers
  et sur le score jour/nuit entre les deux parfums.
- **Profil** : identique ou avec un unisexe = 1.0, unisexe + genré = 0.8,
  masculin + féminin = 0.4, profil manquant = 0.5 (neutre).

Le score final est la somme des 4 composantes pondérées, arrondi à 4
décimales (échelle 0 à 1). Il n'existe pas de seuils numériques figés dans le
code pour qualifier le résultat (« excellent », « risqué »...) : le score et
son détail sont transmis à Claude, qui les formule en langage naturel.

## Rôle base / dessus

Chaque parfum reçoit un score de « lourdeur » (pondéré par son score hiver,
l'inverse de son score été, et un bonus/malus selon que sa famille est
considérée lourde — ambré, boisée, cuir, gourmand, musquée — ou légère —
agrumes, aquatique, vert). Le parfum le plus lourd est proposé en **base**,
l'autre en **dessus**.

`proposer_layering(perfume_id, n)` calcule la compatibilité entre le parfum
de référence et tous les autres parfums de la Knowledge Base, trie par score
décroissant, et retourne les `n` meilleures propositions avec leur rôle.

---

# 2. Rôle de Claude (RAG)

`expliquer_layering()` construit un contexte texte (parfum de référence,
puis pour chaque proposition : rôle, score final, détail des 4 contributions
déjà calculées) et le transmet à Claude avec un système prompt dédié.

**Claude reformule** : il explique pourquoi chaque association fonctionne en
s'appuyant sur les contributions réelles fournies, présente l'ordre
d'application (base puis dessus), et donne des conseils génériques de
technique d'application (laisser sécher entre les deux, doser plus léger le
parfum du dessus, vaporiser sur les vêtements).

**Claude ne décide jamais** : il ne modifie ni le score, ni le classement, ni
le rôle base/dessus — tous fixés par le moteur. Il ne propose que les
parfums présents dans le contexte, sans jamais en inventer, et indique
honnêtement l'absence de proposition pertinente le cas échéant.

Comme pour le chat, chaque appel est indépendant (mode consultation
autonome) : aucun historique de conversation n'est conservé entre deux
demandes de layering.

---

# 3. Endpoint `POST /api/layering`

**Requête** : `perfume_id`, `n` (nombre de propositions souhaitées).

**Réponse** : le texte explicatif de Claude, le parfum de référence, et la
liste des parfums proposés (avec leur score et leur rôle base/dessus).

**Erreurs** : identifiant de parfum invalide → 404 ; configuration serveur
manquante (ex. clé API absente) → 500.

---

# 4. Chargement des données

La Knowledge Base utilisée par le moteur de layering est chargée en mémoire
une seule fois (au premier appel) puis réutilisée pour toutes les requêtes
suivantes, selon le même principe de cache que les autres moteurs
(scoring, recherche sémantique).
