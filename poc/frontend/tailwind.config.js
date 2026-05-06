/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        blu: {
          950: '#060b14',
          900: '#0d1524',
          800: '#111e30',
          700: '#182638',
          600: '#1a2d45',
          500: '#243d5c',
          400: '#2e4f78',
          primary: '#4A9EFF',
        },
      },
      keyframes: {
        'spin-slow': { to: { transform: 'rotate(360deg)' } },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        'spin-slow': 'spin-slow 1.2s linear infinite',
        shimmer: 'shimmer 2s infinite',
      },
    },
  },
  plugins: [],
}
