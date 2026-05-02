/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0f172a',
        mist: '#e2e8f0',
        coral: '#ff6b4a',
        mint: '#2dbd9d',
      },
      boxShadow: {
        glow: '0 16px 40px rgba(13, 26, 58, 0.15)'
      }
    },
  },
  plugins: [],
}
