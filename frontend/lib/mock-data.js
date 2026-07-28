// Données factices pour valider le rendu et les animations de l'interface,
// sans appel API (voir périmètre du prompt : structure et style uniquement).
// La forme des objets reproduit volontairement celle que l'API FastAPI
// retournera réellement (ParfumRecommande : nom, marque, image_url,
// notes_principales, famille, score_compatibilite, details), pour que le
// prochain prompt (branchement de l'API) n'ait qu'à remplacer la source des
// données, pas la forme des composants.

// Trois parfums réels de la Knowledge Base (vraies URLs Luckyscent, pour
// tester l'affichage réel des images), plus un sans image pour tester le
// fallback (~9% des parfums de la Knowledge Base n'ont pas d'Image URL).
export const PARFUMS_EXEMPLE = [
  {
    id: 0,
    nom: "Bois d'Hiver",
    marque: "Ex Nihilo",
    concentration: "Eau de Parfum",
    image_url:
      "https://static.luckyscent.com/images/products/72000.jpg?width=400",
    notes_principales: [
      "poivre rose",
      "cardamome",
      "héliotrope",
      "cyclamen",
      "cèdre blanc",
      "santal",
    ],
    famille: "boise",
    profil: "unisex",
    score_compatibilite: 0.87,
    details: {
      notes: 0.31,
      famille: 0.25,
      saison: 0.16,
      moment: 0.09,
      profil: 0.06,
    },
  },
  {
    id: 1,
    nom: "Sola Parfum",
    marque: "Di Ser",
    concentration: "Parfum",
    image_url:
      "https://static.luckyscent.com/images/products/788011.jpg?width=400",
    notes_principales: [
      "lavande",
      "yuzu",
      "citronnelle",
      "magnolia",
      "géranium",
      "jasmin",
    ],
    famille: "floral",
    profil: "unisex",
    score_compatibilite: 0.74,
    details: {
      notes: 0.24,
      famille: 0.18,
      saison: 0.15,
      moment: 0.09,
      profil: 0.08,
    },
  },
  {
    id: 2,
    nom: "Koala",
    marque: "Zoologist",
    concentration: "Extrait de Parfum",
    // URL volontairement absente : sert à valider le fallback élégant.
    image_url: "",
    notes_principales: [
      "eucalyptus",
      "bonbons de miel mentholé",
      "mimosa",
      "thé noir",
      "géranium",
      "encens",
    ],
    famille: "oriental_ambre",
    profil: "unisex",
    score_compatibilite: 0.69,
    details: {
      notes: 0.2,
      famille: 0.18,
      saison: 0.14,
      moment: 0.11,
      profil: 0.06,
    },
  },
];

// Chips de suggestion (maquette). "layering" est désactivé : hors MVP
// (voir Docs/MVP_SCOPE.md — Layering Engine reporté).
export const SUGGESTIONS_EXEMPLE = [
  { id: "fraicheur", label: "Une alternative plus fraîche", disabled: false },
  {
    id: "layering",
    label: "Suggérer un layering",
    disabled: true,
    tooltip: "Bientôt disponible",
  },
  { id: "pourquoi", label: "Pourquoi ce choix ?", disabled: false },
];

// Conversation factice affichée au chargement, pour visualiser les deux
// variantes de bulles (assistant / utilisateur) et l'intégration d'un
// PerfumeCard + d'une PerfumeGallery dans le fil de discussion.
export const CONVERSATION_EXEMPLE = [
  {
    id: "m1",
    role: "user",
    contenu: "Je cherche un parfum boisé et élégant pour un dîner d'hiver.",
  },
  {
    id: "m2",
    role: "assistant",
    contenu:
      "Excellente demande pour une soirée hivernale. **Bois d'Hiver** d'Ex Nihilo est mon premier choix : il incarne parfaitement la famille boisée recherchée, avec une élégance discrète tout à fait adaptée à un dîner.",
    parfumPrincipal: PARFUMS_EXEMPLE[0],
  },
  {
    id: "m3",
    role: "assistant",
    contenu: "Voici deux autres pistes, dans des registres différents :",
    galerie: [PARFUMS_EXEMPLE[1], PARFUMS_EXEMPLE[2]],
  },
];
