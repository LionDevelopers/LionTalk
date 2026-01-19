import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',

  // 1. Disable source maps in production to save memory and prevent "WorkerError"
  productionBrowserSourceMaps: false,

  // 2. Only enable Docker polling in development, not in production builds
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      };
    }
    return config;
  },
  
  // Optional: If you use <Image /> components, you must disable optimization for static exports
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

