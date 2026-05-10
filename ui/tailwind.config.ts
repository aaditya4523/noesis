import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-body)", "ui-sans-serif", "system-ui"],
        display: ["var(--font-display)", "ui-sans-serif", "system-ui"],
        artifact: ["var(--font-artifact)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"]
      },
      boxShadow: {
        fine: "0 18px 60px rgba(20, 24, 31, 0.08)",
        line: "0 0 0 1px rgba(20, 24, 31, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
