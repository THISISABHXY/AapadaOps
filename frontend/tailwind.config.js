/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Government & Operations Palette (Restrained, professional, high contrast)
        gov: {
          surface: '#f8fafc',      // Clean slate canvas
          panel: '#ffffff',        // Crisp white functional cards
          border: '#e2e8f0',       // Subtle borders
          'border-strong': '#cbd5e1',
          header: '#0f172a',       // Deep navy/slate header
          text: '#0f172a',         // Primary readable text
          muted: '#64748b',        // Muted labels
        },
        // Restrained Governance Green accents
        emeraldgov: {
          50: '#f0fdf4',
          100: '#dcfce7',
          60: '#bbf7d0',
          500: '#22c55e',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        // Standard Government Disaster Alert Tiers (IMD / CND / OSDMA)
        alert: {
          normal: '#166534',       // Green: No warning / Safe
          watch: '#ca8a04',        // Yellow: Be updated / Advisory
          warning: '#ea580c',      // Orange: Be prepared
          severe: '#b91c1c',       // Red: Take action / High emergency
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}
