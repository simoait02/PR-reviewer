import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api\/v1/, ''),
      },
    },
  },
})
