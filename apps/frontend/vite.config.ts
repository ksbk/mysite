// vite.config.ts
import { defineConfig, type UserConfig } from "vite";

// If you use React/Preact later, add the plugin and manualChunks accordingly
// import react from "@vitejs/plugin-react";
// import preact from "@preact/preset-vite";

// -------------------------
// 🔧 shared config knobs
// -------------------------
const DEV_PORT = 5173;
const PREVIEW_PORT = 4173;
const DJANGO_API = "http://127.0.0.1:8000";
// Must match Django STATIC_URL root plus how dist is mounted (STATICFILES_DIRS)
const STATIC_BASE_URL = "/static/dist/";
const OUT_DIR = "../backend/static/dist"; // output to Django static directory
const ENTRY_POINTS = {
  main: "/src/main.ts",
  // admin: "/src/admin.ts",
};
// Add libs if you introduce a framework; keep empty for vanilla TS
const VENDOR_LIBS: string[] = [];

// Optional: Docker/WSL HMR polling toggle
const USE_POLLING = false;

const baseFor = (mode: string) =>
  mode === "production" ? STATIC_BASE_URL : "/";

export default defineConfig(({ mode }: { mode: string }): UserConfig => {
  const isProd = mode === "production";

  return {
    // Match Django STATIC_URL + the dist directory mounted via STATICFILES_DIRS
    base: baseFor(mode),

    // plugins: [react()], // or [preact()]

    server: {
      host: true, // bind 0.0.0.0 (Docker/WSL friendly)
      port: DEV_PORT,
      strictPort: true, // don't auto-bump; Django expects 5173 for HMR
      proxy: {
        // Proxy API requests to Django in dev to avoid CORS
        "/api": {
          target: DJANGO_API,
          changeOrigin: true,
          secure: false,
        },
      },
      hmr: { overlay: true },
      open: mode !== "test",
      // If HMR is flaky in Docker/WSL, enable polling:
      watch: USE_POLLING ? { usePolling: true, interval: 100 } : undefined,
    },

    // `vite preview` to sanity-check built assets locally
    preview: {
      host: true,
      port: PREVIEW_PORT,
      proxy: { "/api": DJANGO_API },
    },

    build: {
      manifest: true, // required for Django to read hashed assets
      outDir: OUT_DIR, // keep output in frontend/dist
      emptyOutDir: true, // clear dist on each build
      assetsDir: "assets", // subfolder for non-entry assets
      sourcemap: !isProd, // useful in staging/dev
      minify: isProd ? "esbuild" : false,
      target: "es2018", // broader browser support than default ESM
      assetsInlineLimit: 4096, // inline small assets to reduce requests

      rollupOptions: {
        input: ENTRY_POINTS,
        output: {
          // simple, stable vendor chunk for long-term caching
          // enable when you add libs
          // manualChunks: { vendor: VENDOR_LIBS },
          // Organized hashed file names for long-term caching
          chunkFileNames: "js/[name]-[hash].js",
          entryFileNames: "js/[name]-[hash].js",
          assetFileNames: (info: any) => {
            const ext = info.name?.split(".").pop()?.toLowerCase() ?? "";
            if (/(png|jpe?g|svg|gif|tiff|bmp|ico|webp)$/.test(ext)) {
              return "images/[name]-[hash][extname]";
            }
            if (/(woff2?|eot|ttf|otf)$/.test(ext)) {
              return "fonts/[name]-[hash][extname]";
            }
            if (ext === "css") {
              return "css/[name]-[hash][extname]";
            }
            return "assets/[name]-[hash][extname]";
          },
        },
      },
    },

    // Only expose non-sensitive build-time constants; prefer import.meta.env VITE_*
    define: {
      __APP_ENV__: JSON.stringify(mode),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    css: {
      devSourcemap: true,
      modules: { localsConvention: "camelCase" },
    },

    // Pre-bundle vendor libs only when you add them
    // optimizeDeps: { include: VENDOR_LIBS },
  };
});
