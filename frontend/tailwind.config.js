/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#9B87F5',
          dark: '#7C67E1',
          light: '#EDE9FE',
        },
        accent: {
          blue: '#93C5FD',
          yellow: '#FDE68A',
        },
        surface: '#FFFFFF',
        page: '#F8F8FC',
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(155, 135, 245, 0.06), 0 10px 15px -3px rgba(155, 135, 245, 0.1)',
        'card-hover': '0 10px 15px -3px rgba(155, 135, 245, 0.1), 0 20px 25px -5px rgba(155, 135, 245, 0.12)',
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.35s ease-out forwards',
        'modal-in': 'modal-in 0.2s ease-out forwards',
      },
    },
  },
  plugins: [],
}
