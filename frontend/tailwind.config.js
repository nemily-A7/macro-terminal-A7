/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: "#111111",
        surface: "#1a1a1a",
        card: "#1e1e1e",
        border: "rgba(255,255,255,0.07)",
        "border-hover": "rgba(255,255,255,0.12)",
        primary: "#e8e8e8",
        secondary: "#888888",
        muted: "#444444",
        accent: "#3b82f6",
        positive: "#22c55e",
        negative: "#ef4444",
        warning: "#f59e0b",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};
