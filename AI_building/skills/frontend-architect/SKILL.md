---
name: frontend-architect
description: >
  Architecture et implémentation de composants frontend soignés avec
  React/Next.js, Shadcn UI et Tailwind. Utiliser dès que la tâche implique de
  créer, refondre ou raffiner un composant, une page, ou d'intégrer un
  composant Shadcn. Déclencheurs : "composant", "page", "UI", "Shadcn",
  "redesign", "frontend", "interface". NE PAS utiliser pour du travail
  backend/data non lié à l'UI.
---

# Frontend Architect

Tu construis des interfaces qui semblent dessinées à la main, jamais générées
par défaut. Ce skill est agnostique du projet : il s'adapte au design system
présent dans le dépôt courant.

## Étape 0 — Découvrir le contexte du projet (obligatoire)

Avant d'écrire la moindre ligne, détecte la stack et le design system réels :

1. Chercher un fichier de direction design : `DESIGN_*.md`, `*_DESIGN_*.md`,
   `design-system*`, ou un dossier `Docs/`. S'il existe, il fait autorité sur
   les tokens (couleurs, typo, espacement, largeurs).
2. Lire `package.json` pour confirmer : JavaScript ou TypeScript ? Next.js
   App Router ou Pages ? Tailwind présent ? Framer Motion ?
3. Inspecter `components/` pour repérer les composants existants et les
   conventions déjà en place (nommage, structure, patterns).
4. Lire `globals.css` / `tailwind.config` pour les variables de thème.

**Ne jamais inventer de tokens ni de stack.** Si aucun design system n'est
trouvé, demander à l'utilisateur ou proposer une direction avant d'implémenter.
Charger le skill `frontend-design` (Anthropic) comme couche esthétique de base.

## Respect de la stack détectée

- Si le projet est en **JSX**, produire du `.jsx` sans annotations de type.
  S'il est en **TypeScript**, typer proprement les props. Suivre l'existant,
  ne jamais imposer l'un ou l'autre.
- Mapper toutes les valeurs de design vers des variables CSS / classes
  Tailwind — jamais de hex, tailles ou espacements codés en dur dans le JSX.
- Respecter la grille d'espacement du projet (souvent 4px : 4, 8, 12, 16, 24…).

## Configuration Shadcn UI

1. Init : `npx shadcn@latest init` (le paquet `shadcn-ui` est déprécié).
2. Brancher le thème Shadcn sur les variables CSS du projet
   (`--background`, `--foreground`, `--accent`…) plutôt que d'écraser les
   composants un par un.
3. Ajouter au besoin : `npx shadcn@latest add button dialog command`.
4. Ne jamais éditer directement `components/ui/` — envelopper ces primitives
   dans des composants applicatifs de plus haut niveau.

## Conventions de composant

- Réutilisables, props simples, valeurs par défaut explicites.
- `cn()` (`lib/utils`) pour composer les classes conditionnelles.
- État local via hooks ; mémoïser (`memo`, `useCallback`) seulement quand un
  vrai coût de rendu le justifie, pas par réflexe.
- Un composant = un fichier ; extraire les sous-parties au-delà de ~150 lignes.
- Étendre un composant existant avant d'en créer un nouveau.

## Accessibilité & responsive

- Mobile-first : concevoir d'abord pour ~380px, puis élargir.
- Cibles tactiles ≥ 44px, focus visibles, `aria-*` sur les éléments custom.
- Respecter `prefers-reduced-motion` pour toute animation.
- Vérifier le contraste texte/fond (WCAG AA au minimum).

## Anti-slop (garde-fous esthétiques)

- Pas de gradients génériques, pas de cartes flottantes surchargées d'ombres,
  pas de symétrie mécanique, pas de sur-usage d'une couleur d'accent.
- Privilégier l'espace négatif, un rythme typographique intentionnel, des
  micro-interactions discrètes. Chaque choix doit être justifiable.