import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    port: 5173,
    host: true,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  },
})