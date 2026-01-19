import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',

  // 1. Add this to enable Turbopack builds (silences the error)
  turbopack: {},

  // 2. Keep this for Docker polling when using Webpack (ignored by Turbopack)
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    };
    return config;
  },
};

export default nextConfig;
