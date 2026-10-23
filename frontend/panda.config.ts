import { defineConfig } from '@pandacss/dev'

export default defineConfig({
  // Whether to use css reset (we already have our own reset.css)
  preflight: false,

  // Where to look for your css declarations
  include: ['./src/**/*.{js,jsx,ts,tsx}'],

  // Files to exclude
  exclude: [],

  // The output directory for your css system
  outdir: 'styled-system',

  // Strict tokens so auto-completion and validation are 100% type-safe
  strictTokens: false,

  theme: {
    extend: {
      tokens: {
        colors: {
          brand: {
            primary: { value: '#123B4A' },
            primaryHover: { value: '#0E303C' },
            primarySoft: { value: '#E8F0F2' },
          },
          surface: {
            bg: { value: '#F7F8FA' },
            card: { value: '#FFFFFF' },
            subtle: { value: '#F1F3F5' },
            border: { value: '#D9DEE3' },
          },
          text: {
            main: { value: '#182126' },
            muted: { value: '#66737A' },
          },
          status: {
            success: { value: '#247A52' },
            warning: { value: '#A66A00' },
            danger: { value: '#B42318' },
            info: { value: '#276678' },
          },
        },
        radii: {
          sm: { value: '4px' },
          md: { value: '6px' },
          lg: { value: '8px' },
        },
        spacing: {
          1: { value: '4px' },
          2: { value: '8px' },
          3: { value: '12px' },
          4: { value: '16px' },
          5: { value: '20px' },
          6: { value: '24px' },
          7: { value: '28px' },
          8: { value: '32px' },
          10: { value: '40px' },
          12: { value: '48px' },
        },
        fontSizes: {
          xs: { value: '12px' },
          sm: { value: '13px' },
          md: { value: '14px' },
          lg: { value: '16px' },
          xl: { value: '18px' },
          '2xl': { value: '22px' },
          '3xl': { value: '28px' },
        },
        shadows: {
          sm: { value: '0 1px 2px rgba(24, 33, 38, 0.06)' },
          md: { value: '0 4px 12px rgba(24, 33, 38, 0.08)' },
        },
      },
    },
  },
})

