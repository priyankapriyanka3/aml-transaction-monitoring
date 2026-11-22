/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Material 3 design tokens extracted from wireframe_01_alert_queue_triage.html
        primary: '#005FCC',
        'on-primary': '#FFFFFF',
        'primary-container': '#E8F1FF',
        'on-primary-container': '#001C3D',
        secondary: '#0066CC',
        'secondary-container': '#D6E4FF',
        'on-secondary-container': '#001B3E',
        tertiary: '#575E71',
        'tertiary-container': '#DBE2F9',
        'on-tertiary-container': '#141B2C',
        background: '#F8F9FA',
        'on-background': '#1A1C1E',
        surface: '#FFFFFF',
        'on-surface': '#1C1C1E',
        'surface-variant': '#EFF1F4',
        'on-surface-variant': '#636366',
        'surface-container-low': '#F4F5F8',
        'surface-container': '#EDEDF2',
        'surface-container-high': '#E7E8ED',
        'surface-container-highest': '#E1E2E7',
        outline: '#D1D1D6',
        'outline-variant': '#E5E5EA',
        'inverse-surface': '#2E3033',
        'inverse-on-surface': '#F1F0F4',
        'inverse-primary': '#A6CAFF',
        'hero-stroke': '#A6CAFF',
        // Compliance semantic status colors
        critical: '#BA1A1A',
        'critical-container': '#FFEBEA',
        'on-critical-container': '#410002',
        warning: '#8A4B00',
        'warning-container': '#FFF0D6',
        'on-warning-container': '#2C1600',
        success: '#1B6D2F',
        'success-container': '#E8F8EE',
        'on-success-container': '#002206',
        info: '#0061A4',
        'info-container': '#D1E4FF',
        'on-info-container': '#001D36',
      },
      fontFamily: {
        sans: ['Inter', 'Roboto', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        // Material 3 typography scale
        'hl': ['24px', { lineHeight: '32px', letterSpacing: '0', fontWeight: '600' }],
        'hm': ['28px', { lineHeight: '36px', letterSpacing: '0', fontWeight: '700' }],
        'tl': ['22px', { lineHeight: '28px', letterSpacing: '0', fontWeight: '600' }],
        'tm': ['18px', { lineHeight: '24px', letterSpacing: '0.15px', fontWeight: '600' }],
        'ts': ['14px', { lineHeight: '20px', letterSpacing: '0.1px', fontWeight: '500' }],
        'bm': ['14px', { lineHeight: '20px', letterSpacing: '0.25px' }],
        'bs': ['12px', { lineHeight: '16px', letterSpacing: '0.4px' }],
        'll': ['14px', { lineHeight: '20px', letterSpacing: '0.1px', fontWeight: '600' }],
        'lm': ['12px', { lineHeight: '16px', letterSpacing: '0.5px', fontWeight: '500' }],
        'ls': ['11px', { lineHeight: '14px', letterSpacing: '0.5px', fontWeight: '600' }],
      },
      spacing: {
        // 4dp baseline grid from design.md §2.4
        '2xs': '2px',
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '20px',
        '2xl': '24px',
        '3xl': '32px',
        '4xl': '48px',
      },
      borderRadius: {
        // Material 3 shape scale from design.md §2.6
        'xs': '4px',
        'sm': '8px',
        DEFAULT: '12px',
        'lg': '16px',
        'xl': '28px',
      },
      minHeight: {
        'touch': '48px', // Minimum 48dp touch target
      },
      minWidth: {
        'touch': '48px',
      },
    },
  },
  plugins: [],
};
