/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: "#0b1e33",
        navy2: "#13294b",
        navy3: "#1c3a63",
        ivory: "#f3ecd9",
        brass: "#c9a227",
        sea: "#2f8f7f",
        ember: "#b3423a",
      },
      fontFamily: {
        display: ["'Playfair Display'", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
