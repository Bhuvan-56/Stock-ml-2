"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

export type Theme = "light" | "dark";

const THEME_STORAGE_KEY = "stockml-theme";

type ThemeContextValue = {
  theme: Theme;
  mounted: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

function resolvePreferredTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  try {
    const persistedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (persistedTheme === "light" || persistedTheme === "dark") {
      return persistedTheme;
    }
  } catch {
    return "light";
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  document.documentElement.style.colorScheme = theme;
}

export const themeScript = `
(() => {
  const storageKey = "${THEME_STORAGE_KEY}";
  try {
    const saved = window.localStorage.getItem(storageKey);
    const theme =
      saved === "light" || saved === "dark"
        ? saved
        : window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light";
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
  } catch {
    document.documentElement.dataset.theme = "light";
    document.documentElement.style.colorScheme = "light";
  }
})();
`;

export function ThemeProvider({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [theme, setThemeState] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const nextTheme = resolvePreferredTheme();
    setThemeState(nextTheme);
    applyTheme(nextTheme);
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) {
      return;
    }

    applyTheme(theme);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    } catch {
      // Ignore localStorage failures and keep the current in-memory theme.
    }
  }, [mounted, theme]);

  const value = useMemo<ThemeContextValue>(
    () => ({
      theme,
      mounted,
      setTheme: setThemeState,
      toggleTheme: () => {
        setThemeState((currentTheme) =>
          currentTheme === "light" ? "dark" : "light"
        );
      }
    }),
    [mounted, theme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (context === null) {
    throw new Error("useTheme must be used within a ThemeProvider.");
  }

  return context;
}
