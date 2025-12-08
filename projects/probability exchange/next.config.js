/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Ignore the packages directory and other non-Next.js folders
  webpack: (config, { isServer }) => {
    config.watchOptions = {
      ignored: ['**/packages/**', '**/archive/**', '**/.venv/**', '**/venv/**'],
    };
    return config;
  },
};

module.exports = nextConfig;
