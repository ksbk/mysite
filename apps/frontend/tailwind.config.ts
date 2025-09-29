import type { Config } from "tailwindcss";

export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx,vue}",
    "../backend/templates/**/*.{html,htm}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
