"use client";

import { MoonStar, SunMedium } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useTheme } from "@/providers/theme-provider";

export function ThemeToggle() {
  const { mounted, theme, toggleTheme } = useTheme();

  const isDark = mounted ? theme === "dark" : false;

  return (
    <Button
      aria-label="Toggle color mode"
      className="h-11 gap-3 rounded-full border border-border/70 bg-card/80 px-4 text-foreground shadow-sm backdrop-blur-md hover:bg-card"
      variant="outline"
      onClick={toggleTheme}
    >
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
        {isDark ? <MoonStar className="h-4 w-4" /> : <SunMedium className="h-4 w-4" />}
      </div>
      <div className="flex flex-col items-start leading-none">
        <span className="text-[11px] font-semibold uppercase tracking-[0.24em] text-muted-foreground">
          Theme
        </span>
        <span className="text-sm font-medium text-foreground">
          {mounted ? (isDark ? "Dark mode" : "Light mode") : "Switch mode"}
        </span>
      </div>
    </Button>
  );
}
