# NAYAAR — Direction Graphique
### Guide de design pour le développement de la plateforme conversationnelle

**Projet :** Maison Nayaar — AI Powered Fragrance Intelligence
**Version :** Design v1.0
**Nature du produit :** Assistant olfactif conversationnel (interface chat)
**Auteur direction :** Al Hassan Ahmed Doumbia

---

## 1. Philosophie visuelle

Nayaar n'est pas un site vitrine ni une boutique classique : c'est un **assistant conversationnel**. L'expérience se déroule dans un fil de discussion, comme un dialogue intime entre le client et un conseiller olfactif.

Le défi de design est donc précis : **faire entrer le luxe dans un format chat**, là où les interfaces conversationnelles sont d'ordinaire fonctionnelles, froides et cliniques.

La réponse tient en trois mots : **luxe lumineux, épuré, minimaliste.**

Principes directeurs :

- **Le vide est un matériau.** L'élégance vient de l'espace, pas de l'accumulation. Marges généreuses, air, respiration.
- **La typographie porte le raffinement.** Le contraste serif / sans-serif fait tout le travail. Peu d'effets, pas de décorations superflues.
- **Le doré est une goutte de parfum, pas le flacon entier.** L'accent ambré s'utilise avec parcimonie, uniquement sur les points d'action.
- **Chaleur, pas froideur.** Le fond crème remplace le blanc clinique. L'interface doit se sentir feutrée, précieuse, calme.

Références d'ambiance : Aesop, Le Labo, Byredo — des maisons où le raffinement naît du silence visuel.

---

## 2. Wordmark (logotype texte)

Nayaar s'écrit en **Lustria**, sa serif de titrage.

**Spécifications :**

- Police : **Lustria**, Regular
- Casse : **Nayaar** (capitale initiale uniquement) — évite les capitales intégrales, trop froides
- Couleur : brun-noir profond `#1C1917` sur fond clair ; doré `#A16207` accepté sur en-tête feutré
- Interlettrage (letter-spacing) : léger, `+0.02em` pour l'espace et la tenue
- Aucune icône obligatoire ; si un signe accompagne le nom, il reste minimal (un point doré, un trait fin)

Le wordmark ne doit jamais être déformé, ombré, ni posé sur un fond chargé.

---

## 3. Typographie

### Familles

| Usage | Police | Origine |
|---|---|---|
| Titres, wordmark, noms de parfums, en-têtes de fiches | **Lustria** (serif) | Google Fonts |
| Corps, messages du chat, interface, boutons, labels | **Mulish** (sans-serif) | Google Fonts |

Import Google Fonts :

```html
<link href="https://fonts.googleapis.com/css2?family=Lustria&family=Mulish:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Échelle typographique

| Rôle | Police | Taille | Poids | Interligne |
|---|---|---|---|---|
| Wordmark / H1 | Lustria | 32–40px | 400 | 1.2 |
| Titre de section / H2 | Lustria | 24–28px | 400 | 1.3 |
| Nom de parfum (fiche) | Lustria | 20px | 400 | 1.3 |
| Message chat (corps) | Mulish | 16px | 400 | 1.6 |
| Label / meta (marque, notes) | Mulish | 13–14px | 500 | 1.4 |
| Bouton | Mulish | 15px | 600 | 1 |
| Petit texte / légende | Mulish | 12px | 400 | 1.5 |

### Règles

- Corps de conversation en **Mulish 16px**, interligne **1.6** : lisibilité maximale, c'est le cœur de l'usage.
- **Lustria uniquement** pour ce qui doit se sentir « éditorial » : noms de parfums, titres, wordmark. Jamais pour de longs paragraphes.
- Pas plus de deux poids visibles simultanément à l'écran.

---

## 4. Palette de couleurs

Palette **volontairement restreinte**. Le minimalisme interdit d'ajouter des couleurs « pour décorer ».

### Couleurs principales

| Nom | Hex | Usage |
|---|---|---|
| **Crème** (fond dominant) | `#FAF7F2` | Fond global de l'application |
| **Crème profond** | `#F3EDE4` | Bulles, cartes, zones secondaires |
| **Brun-noir** (texte) | `#1C1917` | Texte principal, wordmark |
| **Brun doux** | `#57534E` | Texte secondaire, meta, labels |
| **Doré ambré** (accent) | `#A16207` | Éléments visuels d'action, détails précieux |
| **Doré foncé** (liens texte) | `#854D0E` | Liens en texte sur fond clair (contraste ↑) |
| **Ligne / bordure** | `#E7E0D6` | Séparateurs fins, contours discrets |

### Règle d'accent doré

Le doré `#A16207` est **réservé** à :

- le bouton d'envoi du message
- les suggestions cliquables (chips)
- les liens et actions
- de fins détails (point, trait, focus)

Il ne doit **jamais** couvrir de grandes surfaces ni servir de fond de bulle. Pour le texte cliquable sur fond crème, utiliser `#854D0E` (meilleur contraste, accessibilité AA).

---

## 5. Composants de l'interface chat

### Zone de conversation

- Fond : **Crème** `#FAF7F2`
- Largeur de lecture max : **680px**, centrée (confort de lecture éditorial)
- Espacement vertical entre messages : **20–24px**

### Bulle Assistant (Nayaar)

- Fond : **sombre**, brun-noir `#1C1917` — signe la voix feutrée, presque nocturne, de l'assistant
- Texte : **crème clair** `#F5F0E8`, Mulish 16px
- Alignée à gauche
- Coins arrondis doux : `12px`
- Liseré gauche doré `2px #A16207` : ressort nettement sur le fond sombre et signe l'identité de Nayaar
- Détails à l'intérieur (voir fiche parfum ci-dessous) adaptés au fond sombre : surfaces translucides claires, marque en doré

### Bulle Utilisateur

- Fond : **Crème profond** `#F3EDE4`
- Texte : **Brun-noir** `#1C1917`
- Alignée à droite
- Coins arrondis : `12px`

Les deux bulles se distinguent **par le contraste clair / sombre** : la voix de Nayaar est sombre et posée, celle de l'utilisateur claire et légère. Cette opposition crée la hiérarchie de lecture sans recourir à des couleurs saturées.

### Zone de saisie

- Fond : blanc pur `#FFFFFF` ou crème très clair, posé sur le fond crème
- Bordure : `1px #E7E0D6`, focus `1px #A16207`
- Coins arrondis : `16px`
- Bouton d'envoi : rond ou pilule, fond **doré ambré** `#A16207`, icône crème

### Suggestions / chips

- Fond : transparent, bordure `1px #E7E0D6`
- Texte : **Doré foncé** `#854D0E`, Mulish 14px 500
- Survol : fond `#F3EDE4`, bordure `#A16207`
- Coins : pilule (`999px`)

### Fiche parfum (dans le fil)

Petit objet éditorial affiché en réponse, **à l'intérieur de la bulle sombre de Nayaar**. C'est là que le luxe se voit le plus.

- Carte fond translucide clair `rgba(255,255,255,0.05)`, bordure `1px rgba(245,240,232,0.14)`, arrondi `12px`, padding `20px`
- **Nom du parfum** : Lustria 20px, crème clair `#F5F0E8`
- **Marque** : Mulish 13px 500, **doré** `#A16207`, en capitales espacées (`letter-spacing +0.08em`)
- **Notes** : chips translucides claires, texte `#D9D0C4`
- **Score / compatibilité** : barre fine, remplissage doré `#A16207` sur piste translucide
- Un seul accent doré structurant par carte

> Note : si une fiche parfum est un jour affichée hors bulle (sur fond crème), utiliser la variante claire — carte `#F3EDE4`, bordure `#E7E0D6`, texte brun-noir.

---

## 6. Espacement & mise en page

L'espace est la signature. Système d'espacement basé sur **4px**.

| Token | Valeur |
|---|---|
| `space-xs` | 4px |
| `space-sm` | 8px |
| `space-md` | 16px |
| `space-lg` | 24px |
| `space-xl` | 40px |
| `space-2xl` | 64px |

Règles :

- Marges latérales généreuses sur desktop (min `40px`), l'interface ne colle jamais aux bords.
- Rembourrage interne des bulles : `12px 16px`.
- Ne jamais entasser : préférer trop d'air que pas assez.

---

## 7. Autres éléments

**Coins arrondis :**

| Élément | Rayon |
|---|---|
| Bulles / cartes | 12px |
| Zone de saisie | 16px |
| Chips / pilules | 999px |
| Boutons | 999px ou 12px |

**Ombres :** très subtiles ou absentes. Le minimalisme préfère les bordures fines aux ombres portées. Si ombre : `0 1px 3px rgba(28,25,23,0.06)`, jamais plus.

**Icônes :** style linéaire, trait fin (`1.5px`), jeu cohérent (ex. Lucide, Phosphor light). Couleur brun doux `#57534E` au repos, doré `#A16207` si actives.

**Animations :** discrètes et lentes. Apparition des messages en fondu doux (`200–300ms ease-out`). Rien de brusque — le luxe est calme.

---

## 8. Design tokens (prêts pour Claude Code)

```css
:root {
  /* Couleurs */
  --color-bg:            #FAF7F2;
  --color-surface:       #F3EDE4;
  --color-text:          #1C1917;
  --color-text-muted:    #57534E;
  --color-accent:        #A16207;
  --color-accent-link:   #854D0E;
  --color-border:        #E7E0D6;
  --color-input-bg:      #FFFFFF;

  /* Bulle assistant sombre */
  --color-assistant-bg:      #1C1917;
  --color-assistant-text:    #F5F0E8;
  --color-assistant-muted:   #D9D0C4;
  --color-assistant-accent:  #E8B96A;   /* doré éclairci pour texte sur sombre */
  --color-on-dark-surface:   rgba(255,255,255,0.05);
  --color-on-dark-border:    rgba(245,240,232,0.14);

  /* Typographie */
  --font-serif: 'Lustria', Georgia, serif;
  --font-sans:  'Mulish', system-ui, sans-serif;

  /* Espacement */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 40px;
  --space-2xl: 64px;

  /* Rayons */
  --radius-bubble: 12px;
  --radius-input:  16px;
  --radius-pill:   999px;

  /* Ombres */
  --shadow-soft: 0 1px 3px rgba(28,25,23,0.06);

  /* Layout */
  --chat-max-width: 680px;
}
```

---

## 9. Résumé de la direction

> Nayaar est un dialogue feutré sur fond crème. La voix de l'assistant s'incarne dans des bulles sombres, posées et nocturnes, tandis que les messages du client restent clairs et légers — le contraste clair/sombre fait toute la hiérarchie. La serif Lustria porte le nom et les parfums avec une élégance éditoriale ; la sans-serif Mulish assure un confort de lecture absolu. Le doré ambré n'apparaît que pour agir ou signer — un bouton, une suggestion, un liseré, une marque. L'espace fait le luxe. Rien ne crie ; tout respire.
