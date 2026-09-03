/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#f8fafc",
        surface: "#ffffff",
        "surface-card": "#ffffff",
        "surface-hover": "#f1f5f9",
        border: "#e2e8f0",
        "border-subtle": "#f1f5f9",
        primary: {
          DEFAULT: "#4f46e5",
          hover: "#4338ca",
          light: "#e0e7ff",
          subtle: "#eef2ff",
        },
        accent: {
          DEFAULT: "#059669",
          light: "#d1fae5",
          subtle: "#ecfdf5",
        },
        warning: {
          DEFAULT: "#d97706",
          light: "#fef3c7",
        },
        danger: {
          DEFAULT: "#e11d48",
          light: "#ffe4e6",
        },
        slate: {
          75: "#f4f6f9",
        }
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Outfit", "Inter", "sans-serif"],
      },
      boxShadow: {
        "card-sm": "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)",
        "card-md": "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)",
        "card-hover": "0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -4px rgba(0, 0, 0, 0.05)",
      },
    },
  },
  plugins: [],
};
