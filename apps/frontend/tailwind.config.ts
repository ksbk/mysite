import type { Config } from "tailwindcss";

export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx,css,scss}",
    "../../backend/templates/**/*.{html,txt}",
    "../../backend/apps/**/*/templates/**/*.{html,txt}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
