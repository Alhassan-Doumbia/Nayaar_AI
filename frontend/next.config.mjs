/** @type {import('next').NextConfig} */
const nextConfig = {
  // Autorise l'accès en dev (HMR, ressources internes Next) depuis l'IP
  // réseau locale du poste — nécessaire pour tester l'app depuis un
  // téléphone sur le même Wi-Fi. Next.js 16 bloque par défaut les
  // ressources de dev demandées depuis une origine autre que localhost
  // (protection anti-DNS-rebinding). À mettre à jour si l'IP change
  // (voir `ipconfig`, ligne "Adresse IPv4").
  allowedDevOrigins: ["192.168.1.16"],
  images: {
    // Les images de parfums de la Knowledge Base viennent toutes du même
    // hôte (static.luckyscent.com, format /images/products/ID.jpg?width=...).
    // "search" est volontairement omis : la query string (?width=...&404=...)
    // varie selon les fiches, on ne veut pas la contraindre à une valeur exacte.
    remotePatterns: [
      {
        protocol: "https",
        hostname: "static.luckyscent.com",
        pathname: "/images/products/**",
      },
    ],
  },
};

export default nextConfig;
