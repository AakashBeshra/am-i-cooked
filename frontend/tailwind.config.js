/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        charcoal: {
          950: "#0a0a0d",
          900: "#111114",
          800: "#17171c",
          700: "#202028",
          600: "#2a2a34",
        },
        ember: {
          50:  "#fff6ed",
          100: "#ffe8d5",
          200: "#ffc9a5",
          300: "#ffa874",
          400: "#ff803c",
          500: "#ff5c16",
          600: "#f03e0c",
          700: "#c72b0c",
          800: "#9e2412",
          900: "#7f2012",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "Segoe UI", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(255,92,22,0.55)",
        "glow-lg": "0 0 80px -20px rgba(255,92,22,0.7)",
      },
      keyframes: {
        flicker: {
          "0%,100%": { opacity: "1" },
          "45%": { opacity: "0.85" },
          "47%": { opacity: "0.55" },
          "49%": { opacity: "0.95" },
        },
        floaty: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        flicker: "flicker 3s infinite",
        floaty: "floaty 4s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
      },
    },
  },
  plugins: [],
};
