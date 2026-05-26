import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        popover: "hsl(var(--popover))",
        "popover-foreground": "hsl(var(--popover-foreground))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        secondary: "hsl(var(--secondary))",
        "secondary-foreground": "hsl(var(--secondary-foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        accent: "hsl(var(--accent))",
        "accent-foreground": "hsl(var(--accent-foreground))",
        destructive: "hsl(var(--destructive))",
        "destructive-foreground": "hsl(var(--destructive-foreground))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))"
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
        "3xl": "2rem"
      },
      boxShadow: {
        soft: "0 18px 45px rgba(9, 37, 61, 0.08)"
      },
      fontFamily: {
        body: ["var(--font-body)"],
        display: ["var(--font-display)"]
      },
      backgroundImage: {
        spotlight:
          "radial-gradient(circle at top left, rgba(40, 104, 113, 0.18), transparent 35%), radial-gradient(circle at top right, rgba(233, 136, 73, 0.18), transparent 26%), linear-gradient(180deg, rgba(255,255,255,0.92) 0%, rgba(245, 240, 229, 0.85) 100%)"
      }
    }
  },
  plugins: []
};

export default config;
