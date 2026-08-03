import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// During development the React app runs on port 5173. Any request it makes to
// /api or /uploads is quietly forwarded to the backend on port 8000, so the
// browser thinks everything is one website (no CORS issues to worry about).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000',
    },
  },
})
