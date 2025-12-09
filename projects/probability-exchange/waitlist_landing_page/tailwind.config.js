/** @type {import("tailwindcss").Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brandPrimary: '#5C6BC0', // Example: a shade of indigo
        brandSecondary: '#7986CB',
        // Define other custom colors
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // Example: Add a sans-serif font
        mono: ['IBM Plex Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}