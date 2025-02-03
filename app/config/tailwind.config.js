const plugin = require('tailwindcss/plugin')
const { light, dark } = require('./theme/colors')

const toRem = px => `${px / 16}rem`

const SEMANTIC_TOKENS = {
  'app-background': 0,
  'subtle-background': 1,
  'ui-element-background': 2,
  'hovered-ui-element-background': 3,
  'selected-ui-element-background': 4,
  'subtle-border-and-separator': 5,
  'ui-element-border-and-focus': 6,
  'hovered-ui-element-border': 7,
  'solid-background': 8,
  'hovered-solid-background': 9,
  'low-contrast-text': 10,
  'high-contrast-text': 11
}

// Property configurations for different types of utilities
const PROPERTY_TYPES = {
  'bg': 'backgroundColor',
  'text': 'color',
  'border': 'borderColor',
  'ring': '--tw-ring-color', // Fixed to ensure `--tw-ring-color` is updated
  'divide': 'borderColor',
  'outline': 'outlineColor',
  'from': 'gradientColorStops',
  'via': 'gradientColorStops',
  'to': 'gradientColorStops'
}

function generateThemeColors(colors) {
  const variables = {}
  Object.entries(colors).forEach(([colorName, shades]) => {
    Object.entries(SEMANTIC_TOKENS).forEach(([token, shadeIndex]) => {
      const shade = shades[shadeIndex]
      if (colorName === 'primary') {
        variables[`--${token}`] = shade
      } else {
        variables[`--${token}-${colorName}`] = shade
      }
    })
  })
  return variables
}

const semanticColors = plugin(function({ addBase, addUtilities }) {
  // Add CSS Custom Properties (variables)
  addBase({
    ':root': {
      ...generateThemeColors(light),
    },
    '.dark': {
      ...generateThemeColors(dark)
    },
    'html': {
      'height': '100dvh',
      'min-height': '100dvh',
      'display': 'grid',
      'font-family': 'Inter, system-ui, sans-serif',
      'font-optical-sizing': 'auto',
      'font-feature-settings': '"cv02", "cv03", "cv04", "cv11"',
      '-webkit-font-smoothing': 'antialiased',
      '-moz-osx-font-smoothing': 'grayscale',
    },
    'body': {
      'height': '100dvh',
      'background-color': 'var(--app-background)',
      'color': 'var(--high-contrast-text)',
    }
  })

  const utilities = {}

  // Generate utilities for each property type
  Object.entries(PROPERTY_TYPES).forEach(([prefix, property]) => {
    // Helper for gradient properties
    const getGradientValue = (token, type) => {
      if (type === 'from') return `var(--${token}) var(--tw-gradient-from-position)`;
      if (type === 'via') return `var(--${token}) var(--tw-gradient-via-position)`;
      if (type === 'to') return `var(--${token}) var(--tw-gradient-to-position)`;
      return `var(--${token})`;
    }

    // Primary color utilities
    Object.keys(SEMANTIC_TOKENS).forEach(token => {
      if (['from', 'via', 'to'].includes(prefix)) {
        utilities[`.${prefix}-${token}`] = {
          '--tw-gradient-stops': `var(--tw-gradient-from), var(--tw-gradient-to)`,
          [`--tw-gradient-${prefix}`]: getGradientValue(token, prefix)
        }
      } else {
        // Ensure `ring` updates `--tw-ring-color`
        if (prefix === 'ring') {
          utilities[`.${prefix}-${token}`] = {
            '--tw-ring-color': `var(--${token})`
          }
        } else {
          utilities[`.${prefix}-${token}`] = {
            [property]: `var(--${token})`
          }
        }
      }
    })

    // Color variant utilities
    Object.keys(light).forEach(colorName => {
      if (colorName !== 'primary') {
        Object.keys(SEMANTIC_TOKENS).forEach(token => {
          if (['from', 'via', 'to'].includes(prefix)) {
            utilities[`.${prefix}-${token}-${colorName}`] = {
              '--tw-gradient-stops': `var(--tw-gradient-from), var(--tw-gradient-to)`,
              [`--tw-gradient-${prefix}`]: getGradientValue(`${token}-${colorName}`, prefix)
            }
          } else {
            // Ensure `ring` updates `--tw-ring-color`
            if (prefix === 'ring') {
              utilities[`.${prefix}-${token}-${colorName}`] = {
                '--tw-ring-color': `var(--${token}-${colorName})`
              }
            } else {
              utilities[`.${prefix}-${token}-${colorName}`] = {
                [property]: `var(--${token}-${colorName})`
              }
            }
          }
        })
      }
    })
  })

  addUtilities(utilities)
})

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'selector',
  content: [
    "../**/*.py",
    { raw: '.dark' }
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      // Default Inter configuration
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
        black: '900',
      },
      spacing: {
        '2xs': toRem(3),    // 0.1875rem
        'xs': toRem(5),     // 0.3125rem
        'sm': toRem(8),     // 0.5rem
        'md': toRem(13),    // 0.8125rem
        'lg': toRem(21),    // 1.3125rem
        'xl': toRem(34),    // 2.125rem
        '2xl': toRem(55),   // 3.4375rem
        '3xl': toRem(89),   // 5.5625rem
        '4xl': toRem(144),  // 9rem
      }
    }
  },
  plugins: [
    semanticColors
  ],
}
