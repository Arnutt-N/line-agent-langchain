import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  css: {
    postcss: './postcss.config.js',
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['lucide']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://your-vercel-app.vercel.app' 
          : 'http://localhost:8000',
        changeOrigin: true
      },
      '/webhook': {
        target: process.env.NODE_ENV === 'production' 
          ? 'https://your-vercel-app.vercel.app' 
          : 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: process.env.NODE_ENV === 'production' 
          ? 'wss://your-vercel-app.vercel.app' 
          : 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 4173,
    host: true
  }
})