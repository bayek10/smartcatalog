import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // No need for output: 'export' since we're using SSR
  // No need for unoptimized images since we're not doing static export
  
  // Optional: Configure domains for next/image if needed
  images: {
    unoptimized: true,
  }
};

export default nextConfig;
