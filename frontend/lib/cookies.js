// Utilitaires cookie minimalistes pour la persistance du session_id du chat.
// Volontairement PAS localStorage (consigne explicite) : un cookie survit
// aussi aux rechargements de page côté navigateur, sans dépendance externe.

export function obtenirCookie(nom) {
  if (typeof document === "undefined") return null; // rendu serveur : pas de cookie accessible
  const ligne = document.cookie
    .split("; ")
    .find((entree) => entree.startsWith(`${nom}=`));
  return ligne ? decodeURIComponent(ligne.split("=")[1]) : null;
}

export function definirCookie(nom, valeur, dureeJours) {
  if (typeof document === "undefined") return;
  const expiration = new Date();
  expiration.setDate(expiration.getDate() + dureeJours);
  document.cookie = `${nom}=${encodeURIComponent(valeur)}; expires=${expiration.toUTCString()}; path=/; SameSite=Lax`;
}
