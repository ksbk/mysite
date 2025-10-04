import { defineConfig, type UserConfig } from "vite";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, "../backend/static/dist");

// Single Vite config aligned with Django static paths
export default defineConfig(({ mode }): UserConfig => {
  return {
    // Match Django STATIC_URL + dist folder
    base: "/static/dist/",

    server: {
      host: true,
      port: 5173,
      strictPort: true,
    },

    build: {
      manifest: true,
      outDir: OUT_DIR,
      emptyOutDir: true,
      assetsDir: "assets",
      rollupOptions: {
        input: resolve(__dirname, "src/main.ts"),
        output: {
          chunkFileNames: "js/[name]-[hash].js",
          entryFileNames: "js/[name]-[hash].js",
          assetFileNames: ({ name }) => {
            const ext = name?.split(".").pop()?.toLowerCase() ?? "";
            if (/(png|jpe?g|svg|gif|tiff|bmp|ico|webp)$/.test(ext))
              return "images/[name]-[hash][extname]";
            if (/(woff2?|eot|ttf|otf)$/.test(ext))
              return "fonts/[name]-[hash][extname]";
            if (ext === "css") return "css/[name]-[hash][extname]";
            return "assets/[name]-[hash][extname]";
          },
        },
      },
    },
  };
});
