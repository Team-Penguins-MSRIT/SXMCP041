/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      colors: {
        abyss: '#050505',
      },
      backgroundImage: {
        'gradient-active':
          'linear-gradient(135deg, rgb(99 102 241 / 0.35), rgb(139 92 246 / 0.25))',
      },
      boxShadow: {
        glow: '0 0 32px rgb(99 102 241 / 0.25)',
        'glow-sm': '0 0 16px rgb(99 102 241 / 0.2)',
      },
    },
  },
  plugins: [],
}
