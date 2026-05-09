import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:80',
        changeOrigin: true,
      },
      // Proxy Keycloak auth endpoints but NOT /auth/callback (React handles that)
      '/auth/realms': {
        target: 'http://localhost:80',
        changeOrigin: true,
      },
      '/auth/admin': {
        target: 'http://localhost:80',
        changeOrigin: true,
      },
      '/auth/resources': {
        target: 'http://localhost:80',
        changeOrigin: true,
      },
    },
  },
})
