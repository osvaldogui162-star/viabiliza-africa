import type { NextConfig } from "next";

const backendUrl = process.env.BACKEND_URL ?? "http://127.0.0.1:5000";

const nextConfig: NextConfig = {
  // Permite aceder ao Next em desenvolvimento via IP da rede (telemóvel / QR)
  allowedDevOrigins: [
    "192.168.1.185",
    "192.168.1.105",
    "127.0.0.1",
    "localhost",
  ],
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
