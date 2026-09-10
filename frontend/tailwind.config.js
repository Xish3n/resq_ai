/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          950: "#080D18",
          900: "#0B1220",
          800: "#111A2E",
          700: "#182238",
          600: "#22304A",
          500: "#324364",
        },
        ink: {
          100: "#EEF2FA",
          300: "#C6D0E4",
          500: "#93A3C2",
          700: "#5C6A8A",
        },
        signal: {
          amber: "#F2994A",
          cyan: "#38BDF8",
          teal: "#2AB6A6",
        },
        risk: {
          low: "#2FBF71",
          medium: "#F5A623",
          high: "#F2734B",
          critical: "#E14B4B",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      boxShadow: {
        panel: "0 1px 0 0 rgba(255,255,255,0.03) inset",
      },
    },
  },
  plugins: [],
};
