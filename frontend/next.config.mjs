/** @type {import('next').NextConfig} */
const nextConfig = {
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
