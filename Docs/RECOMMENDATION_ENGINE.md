# RECOMMENDATION ENGINE
# Nayaar – Moteur de recommandation

Version : MVP v1.0 (implémenté)
Fichiers : `backend/app/recommendation/scoring.py`, `semantic_search.py`, `hybrid.py`
Route : `POST /api/recommend`

---

# Principe

Le moteur de recommandation ne fait jamais appel à un LLM pour décider.
Il combine deux mécanismes complémentaires, tous deux déterministes :

1. un **moteur de règles** (scoring) qui compare les préférences explicites
   de l'utilisateur aux features de la Knowledge Base ;
2. une **recherche sémantique** (embeddings + FAISS) qui interprète un besoin
   décrit en langage libre.

Le point d'entrée `/api/recommend` (préférences structurées) n'utilise que le
moteur de règles. Le point d'entrée `/api/chat` (texte libre) utilise le
moteur hybride, qui combine les deux.

---

# 1. Moteur de règles (`scoring.py`)

## Entrées (préférences utilisateur)

| Champ | Type | Description |
|---|---|---|
| `notes_aimees` | liste de notes | Notes que le client apprécie |
| `famille_preferee` | famille olfactive | Une des 12 familles connues |
| `saison` | saison | winter / spring / summer / autumn |
| `moment` | moment | day / night |
| `profil` | profil | masculine / feminine / unisex |
| `marques_exclues` | liste de marques | Marques à exclure (insensible à la casse) |

Chaque champ non renseigné est neutre : il ne pénalise pas le score.

## Pondération (somme = 1.0)

| Composante | Poids |
|---|---|
| Notes | 0.35 |
| Famille | 0.25 |
| Saison | 0.20 |
| Moment | 0.10 |
| Profil | 0.10 |

## Calcul de chaque composante

- **Notes** : rappel (recall) — `notes aimées ∩ notes du parfum / notes aimées`,
  après normalisation via le vocabulaire (`notes_vocabulary.json`).
- **Famille** : 1.0 si la famille dominante correspond, 0.5 si la famille est
  présente parmi les catégories du parfum, 0.0 sinon.
- **Saison** : score direct du parfum sur la saison demandée (ex. `winter_score`).
- **Moment** : score direct du parfum sur le moment demandé (`day_score` /
  `night_score`).
- **Profil** : 1.0 si profils identiques, 0.5 si l'un des deux est unisexe,
  0.0 en cas d'opposition masculin/féminin.

## Combinaison finale

1. Calcul des 5 scores bruts (chacun dans `[0, 1]`).
2. **Filtre anti-contresens saisonnier** : si une saison est demandée et que le
   score saison est inférieur à 0.50, une pénalité quadratique
   `(score_saison / 0.50)²` est appliquée à l'ensemble du score pondéré —
   évite qu'un parfum d'hiver lourd ressorte en été grâce à ses seules notes.
3. `score_final = Σ (score_composante × poids_composante × pénalité)`, arrondi
   à 4 décimales.

`recommander()` exclut d'abord les marques interdites, puis score et trie tous
les parfums restants, et retourne les `n` meilleurs.

---

# 2. Recherche sémantique (`semantic_search.py`)

| Paramètre | Valeur |
|---|---|
| Modèle d'embedding | `all-MiniLM-L6-v2` (sentence-transformers, 384 dimensions) |
| Texte encodé | `profil_text` (texte de synthèse par parfum) |
| Index | FAISS `IndexFlatL2`, recherche exacte |
| Vecteurs | Normalisés L2 avant indexation et avant recherche |
| Sortie | Distance L2 sur vecteurs normalisés, dans `[0, 2]` (0 = identique) |

Le modèle, l'index et le mapping (position → parfum) sont chargés une seule
fois au démarrage et gardés en mémoire.

---

# 3. Moteur hybride (`hybrid.py`)

Utilisé pour les recherches en texte libre (`/api/chat`) :

1. Récupère un pool de 50 candidats via la recherche sémantique.
2. Extrait des préférences structurées du texte libre par recherche de
   mots-clés (familles, saison, moment...) — sans LLM.
3. Re-score chaque candidat du pool avec le moteur de règles complet.
4. Convertit la distance FAISS en similarité :
   `score_semantique = max(0, 1 - distance / 2)`.
5. Combine à parts égales :
   `score_hybride = 0.5 × score_semantique + 0.5 × score_regles`.
6. Trie par score hybride décroissant et retourne les `n` meilleurs, avec le
   détail complet (score sémantique, distance, score de règles, contributions).

---

# 4. Endpoint `POST /api/recommend`

N'utilise que le moteur de règles.

**Requête**

```
notes_aimees: liste de notes (défaut [])
famille_preferee: famille olfactive (optionnel)
saison: saison (optionnel)
moment: moment (optionnel)
profil: profil (optionnel)
marques_exclues: liste de marques (défaut [])
n: nombre de résultats (1 à 50, défaut 5)
```

**Réponse**

Liste de parfums recommandés, chacun avec : identifiant, nom, marque, image,
notes principales, famille, score de compatibilité et détail des
contributions pondérées (notes, famille, saison, moment, profil).

Une préférence invalide (famille/saison/moment/profil inconnu) renvoie une
erreur 400 explicite plutôt qu'un résultat silencieusement faux.
