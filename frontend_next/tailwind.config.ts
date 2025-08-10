import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#0e1117',
          card: '#141821',
          accent: '#00C2A8',
        },
      },
    },
  },
  plugins: [],
}

export default config


