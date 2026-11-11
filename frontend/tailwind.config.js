/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Strict Government Operations Palette (Prompt 3 Mandate)
        bg: {
          warm: '#F6F5F0',          // Warm neutral background
          surface: '#FFFFFF',       // Clean functional white card surface
          subtle: '#EFEFEA',        // Subtle nested background
        },
        ink: {
          primary: '#202B32',      // Deep slate primary ink
          secondary: '#4A5860',    // Secondary readable text
          muted: '#71877C',        // Muted labels & timestamps (Sage)
        },
        forest: {
          DEFAULT: '#365B4A',      // Forest green primary brand & verified actions
          dark: '#2A473A',
          light: '#477460',
          subtle: '#EBF1EE',       // Light green tint for badges & selected states
        },
        sage: {
          DEFAULT: '#71877C',      // Neutral accent & secondary indicators
          light: '#A3B4AB',
          subtle: '#F0F3F1',
        },
        amber: {
          DEFAULT: '#D7A65B',      // Advisory / Watch / Needs verification
          dark: '#B8863A',
          subtle: '#FAF4E8',
        },
        emergency: {
          DEFAULT: '#B64C45',      // Critical / Life safety / Rejection / Emergency red
          dark: '#963A34',
          subtle: '#F8ECEB',
        },
        line: {
          DEFAULT: '#E7E8E3',      // Subtle border line
          dark: '#D5D7CF',        // Interactive border on hover/focus
        },
      },
      fontFamily: {
        sans: ['"Source Sans 3"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      boxShadow: {
        // Subtle, practical non-gimmick shadows
        'sm': '0 1px 2px 0 rgba(32, 43, 50, 0.05)',
        'DEFAULT': '0 1px 3px 0 rgba(32, 43, 50, 0.08), 0 1px 2px -1px rgba(32, 43, 50, 0.08)',
        'md': '0 4px 6px -1px rgba(32, 43, 50, 0.07), 0 2px 4px -2px rgba(32, 43, 50, 0.07)',
      },
      borderRadius: {
        'sm': '3px',
        'DEFAULT': '4px',
        'md': '6px',
        'lg': '8px',
      },
    },
  },
  plugins: [],
}
