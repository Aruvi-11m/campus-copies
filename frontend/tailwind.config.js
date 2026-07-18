/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'campus-blue': '#1e3a8a',
        'campus-light': '#eff6ff',
      }
    },
  },
  plugins: [],
}
