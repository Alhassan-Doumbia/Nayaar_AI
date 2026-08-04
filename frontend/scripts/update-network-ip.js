#!/usr/bin/env node
// Détecte l'IP réseau locale de la machine et met à jour automatiquement :
//   - frontend/.env.local  (NEXT_PUBLIC_API_URL)
//   - backend/.env         (CORS_ORIGINS)
//
// Objectif : pouvoir faire une démo sur n'importe quel Wi-Fi (salle,
// hotspot mobile...) sans jamais éditer une IP à la main. Lancé
// automatiquement avant `npm run dev` (voir "predev" dans package.json),
// ou manuellement : node scripts/update-network-ip.js

const fs = require("fs");
const os = require("os");
const path = require("path");

const DOSSIER_FRONTEND = path.join(__dirname, "..");
const DOSSIER_RACINE = path.join(DOSSIER_FRONTEND, "..");
const CHEMIN_ENV_LOCAL = path.join(DOSSIER_FRONTEND, ".env.local");
const CHEMIN_ENV_BACKEND = path.join(DOSSIER_RACINE, "backend", ".env");

const PORT_BACKEND = 8000;
const PORT_FRONTEND = 3000;

// Adaptateurs à ignorer : VPN, machines virtuelles, WSL... faussent souvent
// la détection avec une IP qui ne correspond à aucun réseau Wi-Fi réel.
const MOTIFS_INTERFACES_IGNOREES = /virtual|vethernet|vmware|virtualbox|loopback|tailscale|wsl/i;

/**
 * Retourne la meilleure IPv4 locale trouvée (hors localhost), en
 * préférant les plages privées classiques (Wi-Fi, Ethernet, partage de
 * connexion mobile) aux adaptateurs virtuels.
 */
function detecterIpReseau() {
  const interfaces = os.networkInterfaces();
  const candidates = [];

  for (const [nom, entrees] of Object.entries(interfaces)) {
    if (MOTIFS_INTERFACES_IGNOREES.test(nom)) continue;
    for (const entree of entrees || []) {
      if (entree.family === "IPv4" && !entree.internal) {
        candidates.push(entree.address);
      }
    }
  }

  const adressePrivee = candidates.find((ip) =>
    /^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(ip)
  );
  return adressePrivee || candidates[0] || null;
}

function mettreAJourEnvLocal(ip) {
  const contenu = `# Généré automatiquement par scripts/update-network-ip.js (voir "predev" dans package.json).
# Ne pas éditer à la main : réécrit à chaque \`npm run dev\`.
NEXT_PUBLIC_API_URL=http://${ip}:${PORT_BACKEND}
`;
  fs.writeFileSync(CHEMIN_ENV_LOCAL, contenu, "utf-8");
}

/** Met à jour uniquement la ligne CORS_ORIGINS de backend/.env, sans toucher au reste (clé API...). */
function mettreAJourEnvBackend(ip) {
  if (!fs.existsSync(CHEMIN_ENV_BACKEND)) {
    console.warn(
      "⚠ backend/.env introuvable — CORS_ORIGINS non mis à jour (copier backend/.env.example d'abord)."
    );
    return;
  }

  const ligneCors = `CORS_ORIGINS=http://localhost:${PORT_FRONTEND},http://${ip}:${PORT_FRONTEND}`;
  const contenuActuel = fs.readFileSync(CHEMIN_ENV_BACKEND, "utf-8");
  const regexLigneCors = /^CORS_ORIGINS=.*$/m;

  const nouveauContenu = regexLigneCors.test(contenuActuel)
    ? contenuActuel.replace(regexLigneCors, ligneCors)
    : `${contenuActuel.trimEnd()}\n\n${ligneCors}\n`;

  fs.writeFileSync(CHEMIN_ENV_BACKEND, nouveauContenu, "utf-8");
}

const ip = detecterIpReseau();

if (!ip) {
  console.warn(
    "⚠ Aucune IP réseau détectée (hors localhost) — fichiers inchangés, l'app restera en localhost uniquement."
  );
  process.exit(0);
}

mettreAJourEnvLocal(ip);
mettreAJourEnvBackend(ip);

console.log(`✔ IP réseau détectée : ${ip}`);
console.log(`  frontend/.env.local -> NEXT_PUBLIC_API_URL=http://${ip}:${PORT_BACKEND}`);
console.log(`  backend/.env        -> CORS_ORIGINS mis à jour`);
console.log(
  `\nPense à lancer (ou relancer) le backend avec --host 0.0.0.0 :\n  python main.py   (depuis backend/app/, voir le bloc __main__)\n`
);
