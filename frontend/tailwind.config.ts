import type { Config } from "tailwindcss";

/**
 * Tailwind config bound to the DClaw design-kit tokens.
 *
 * The single source of truth for tokens is `src/styles/brand.css` (CSS
 * custom properties prefixed `--dk-*`). This config exposes them as
 * Tailwind utilities (`bg-brand`, `text-fg-1`, `border-brand`,
 * `shadow-brand`, `rounded-pill`, …). Light mode only — never add a
 * `.dark` class. Prefer semantic aliases over raw palette values.
 */
const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "var(--dk-container-pad)",
      screens: { "2xl": "var(--dk-container-max)" },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        brand: {
          DEFAULT: "var(--dk-purple-700)",
          hover: "var(--dk-purple-800)",
          press: "var(--dk-purple-900)",
          soft: "var(--dk-purple-100)",
          50: "var(--dk-purple-50)",
          100: "var(--dk-purple-100)",
          200: "var(--dk-purple-200)",
          300: "var(--dk-purple-300)",
          400: "var(--dk-purple-400)",
          500: "var(--dk-purple-500)",
          600: "var(--dk-purple-600)",
          700: "var(--dk-purple-700)",
          800: "var(--dk-purple-800)",
          900: "var(--dk-purple-900)",
        },

        ink: "var(--dk-ink)",
        gray: {
          50: "var(--dk-gray-50)",
          100: "var(--dk-gray-100)",
          200: "var(--dk-gray-200)",
          300: "var(--dk-gray-300)",
          400: "var(--dk-gray-400)",
          500: "var(--dk-gray-500)",
          600: "var(--dk-gray-600)",
          700: "var(--dk-gray-700)",
          800: "var(--dk-gray-800)",
          900: "var(--dk-gray-900)",
        },

        bg: {
          DEFAULT: "var(--dk-bg)",
          muted: "var(--dk-bg-muted)",
          tint: "var(--dk-bg-tint)",
          inverse: "var(--dk-bg-inverse)",
        },
        fg: {
          DEFAULT: "var(--dk-fg)",
          1: "var(--dk-fg-1)",
          2: "var(--dk-fg-2)",
          muted: "var(--dk-fg-muted)",
          "on-brand": "var(--dk-fg-on-brand)",
          inverse: "var(--dk-fg-inverse)",
        },
        "border-strong": "var(--dk-border-strong)",
        "border-brand": "var(--dk-border-brand)",

        success: { DEFAULT: "var(--dk-success)", bg: "var(--dk-success-bg)" },
        warning: { DEFAULT: "var(--dk-warning)", bg: "var(--dk-warning-bg)" },
        danger: { DEFAULT: "var(--dk-danger)", bg: "var(--dk-danger-bg)" },
        info: { DEFAULT: "var(--dk-info)", bg: "var(--dk-info-bg)" },
      },

      fontFamily: {
        sans: ["var(--dk-font-sans)"],
        display: ["var(--dk-font-display)"],
        mono: ["var(--dk-font-mono)"],
      },
      letterSpacing: {
        tight: "var(--dk-tracking-tight)",
        snug: "var(--dk-tracking-snug)",
        wide: "var(--dk-tracking-wide)",
      },

      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        xs: "var(--dk-radius-xs)",
        xl: "var(--dk-radius-xl)",
        "2xl": "var(--dk-radius-2xl)",
        pill: "var(--dk-radius-pill)",
      },

      boxShadow: {
        xs: "var(--dk-shadow-xs)",
        sm: "var(--dk-shadow-sm)",
        md: "var(--dk-shadow-md)",
        lg: "var(--dk-shadow-lg)",
        brand: "var(--dk-shadow-brand)",
      },

      transitionTimingFunction: {
        "out-quart": "var(--dk-ease-out)",
        "in-out-quart": "var(--dk-ease-in-out)",
      },
      transitionDuration: {
        fast: "var(--dk-dur-fast)",
        base: "var(--dk-dur-base)",
        slow: "var(--dk-dur-slow)",
      },

      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down var(--dk-dur-base) var(--dk-ease-out)",
        "accordion-up": "accordion-up var(--dk-dur-base) var(--dk-ease-out)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
