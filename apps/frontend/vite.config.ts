import { defineConfig } from "vite";

export default defineConfig(({ mode }) => ({
  server: {
    host: true,
    port: 5173,
    strictPort: false,
  },
  build: {
    manifest: true,
    outDir: "dist",
    rollupOptions: {
      input: "/src/main.ts",
    },
  },
}));
