/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["'Space Grotesk'", "Inter", "sans-serif"],
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
      },
      colors: {
        ink: {
          950: "#05060a",
          900: "#090b12",
          800: "#0e111b",
          700: "#151a28",
          600: "#1d2435",
        },
        brand: {
          DEFAULT: "#2dd4bf",
          dark: "#0d9488",
          glow: "#5eead4",
        },
        accent: {
          DEFAULT: "#8b5cf6",
          cyan: "#22d3ee",
          violet: "#a78bfa",
        },
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(45,212,191,0.15), 0 0 30px -5px rgba(45,212,191,0.35)",
        "glow-violet": "0 0 0 1px rgba(139,92,246,0.15), 0 0 30px -5px rgba(139,92,246,0.35)",
        card: "0 10px 40px -15px rgba(0,0,0,0.6)",
      },
      backgroundImage: {
        "grid-faint":
          "linear-gradient(to right, rgba(148,163,184,0.06) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.06) 1px, transparent 1px)",
        "radial-brand":
          "radial-gradient(circle at 20% 0%, rgba(45,212,191,0.12), transparent 40%), radial-gradient(circle at 90% 10%, rgba(139,92,246,0.12), transparent 40%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease-out both",
        "pulse-glow": "pulse-glow 3s ease-in-out infinite",
        shimmer: "shimmer 1.5s infinite",
      },
    },
  },
  plugins: [],
};
