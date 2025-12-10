import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    // Production optimizations - using esbuild (faster and built-in)
    minify: 'esbuild',
    // Code splitting for optimal loading
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-motion': ['framer-motion'],
          'vendor-charts': ['recharts'],
          'vendor-query': ['@tanstack/react-query'],
        },
      },
    },
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    // Asset optimization
    assetsInlineLimit: 4096, // 4kb - inline smaller assets
    // Source maps for production debugging (optional)
    sourcemap: false, // Set to true if you need source maps in production
    // Target modern browsers for smaller bundles
    target: 'es2015',
  },
  esbuild: {
    // Drop console and debugger in production
    drop: ['console', 'debugger'],
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Preview server configuration
  preview: {
    port: 4173,
    strictPort: false,
  },
})
