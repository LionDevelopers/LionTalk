import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'export',


  // Add this section to enable Polling for Docker (for win/mac users during development)
  webpack: (config) => {
    config.watchOptions = {
      poll: 1000,   // Check for changes every second
      aggregateTimeout: 300, // Delay before rebuilding
    };
    return config;
  },

};

export default nextConfig;
