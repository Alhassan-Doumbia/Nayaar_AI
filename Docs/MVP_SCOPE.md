# MVP SCOPE
# Nayaar – Périmètre du MVP

Version : 1.0

---

# Principe directeur

Le volume d'enrichissement identifié dans `DATA_SOURCES.md` change la donne :
la majorité des champs de la Knowledge Base sont **probabilistes** et coûteux
à générer proprement sur ~2191 parfums.

**Le MVP ne génère donc PAS toutes les features.**
Il en génère un sous-ensemble restreint mais fiable, et construit un moteur
de scoring qui fonctionne réellement dessus, doublé d'une couche
conversationnelle (RAG + Claude).

> Mieux vaut 5 features validées et un moteur qui marche et s'explique,
> que 30 features douteuses et un moteur qu'on ne peut pas justifier.

---

# MUST — le chemin critique

Ces briques constituent le MVP. Sans elles, pas de produit.

| Brique | Détail |
|---|---|
| Dataset nettoyé | Doublons, valeurs manquantes, normalisation, parsing des notes |
| Vocabulaire de notes | Dictionnaire normalisé des notes olfactives — socle du scoring |
| Features de base | `famille`, `notes parsées`, `saison` (4 scores), `moment` (day/night), `profil` (M/F/U) |
| Validation manuelle | Contrôle qualité par échantillonnage de l'enrichissement |
| Moteur de scoring | Similarité notes + famille + filtres saison/moment/profil, **avec explication** |
| Recherche par intention | Besoin décrit → 5 parfums scorés |
| Embeddings + recherche sémantique | sentence-transformers (dim 384) + Supabase/pgvector |
| Recherche hybride | Sémantique (pool) + re-classement par scoring |
| RAG + chat Claude | Claude reformule les résultats du moteur, sans jamais décider |
| API FastAPI | Exposition des moteurs au frontend |
| Interface Next.js | Chat premium (JSX, sans TypeScript) conforme à la maquette |

---

# LATER — hors MVP, assumé

Ces briques sont volontairement reportées. Elles sont séduisantes mais
demandent un socle de features solide ou des données utilisateurs
qui n'existeront pas à temps.

- **Layering Engine** (le chip « Suggérer un layering » est désactivé au MVP)
- Features `style` (elegant, luxury, romantic, powerful…)
- Features `usage` (office, date, party, wedding…)
- Features `climat` (hot/cold/humid/dry weather)
- Features `performances` (projection, sillage, longévité)
- Collaborative Filtering (KNN)
- Profils utilisateurs persistants
- Authentification / comptes clients

---

# Décisions clés

1. **La famille olfactive est dérivée par règles**, à partir du vocabulaire
   de notes — pas par appel LLM. Explicable et reproductible.

2. **Les scores saison / moment sont dérivés par règles**, à partir des
   attributs des notes (ex : agrumes → summer, ambré/boisé → winter).
   Gratuit, déterministe, explicable.

3. **Claude (API Anthropic) ne décide jamais.** Il reçoit les résultats du
   moteur en contexte et les reformule. Il n'invente aucun parfum et ne
   contredit jamais le scoring.

4. **Embeddings découplés du LLM.** Anthropic ne fournit pas de modèle
   d'embeddings : `sentence-transformers` (`all-MiniLM-L6-v2`, dim 384)
   encode en local, Supabase + pgvector stocke et recherche.

5. **Le moteur explique toujours son score.** Non négociable — c'est la
   différenciation du projet et la traduction de sa philosophie
   (« l'IA explique, le moteur décide »). L'interface l'affiche via le
   score de compatibilité et le bouton « Pourquoi ce choix ? ».

6. **Normalisation du score d'affichage.** Le score brut du moteur
   (souvent 0.4–0.6) doit être normalisé pour produire des valeurs
   crédibles à l'écran (ex : 95%), sans casser la promesse premium.

---

# Stack MVP (rappel)

- **Frontend :** Next.js (JavaScript / JSX, sans TypeScript), Tailwind CSS
- **Backend :** FastAPI (Python)
- **Base de données :** Supabase (Postgres + pgvector)
- **Embeddings :** sentence-transformers (`all-MiniLM-L6-v2`, dim 384)
- **LLM conversationnel :** API Claude (Anthropic)
- **Data / notebooks :** Pandas, NumPy, scikit-learn, Matplotlib, Seaborn

---

# Résultat attendu du MVP

Une application de chat premium où l'utilisateur décrit un besoin en langage
naturel et reçoit des recommandations de parfums :

- pertinentes (moteur de scoring + recherche sémantique)
- explicables (score de compatibilité + contributions détaillées)
- reformulées naturellement (Claude, sans pouvoir de décision)

Le tout adossé à la **Nayaar Knowledge Base**, seule source de vérité,
que les moteurs interrogent exclusivement.
