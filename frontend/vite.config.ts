import { defineConfig } from 'vite'

export default defineConfig({
  // React is handled via automatic JSX runtime
  // No plugin needed for Vite 8+ with React 19
  server: {
    port: 5173,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
