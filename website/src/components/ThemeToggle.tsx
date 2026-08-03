import { Desktop, Moon, Sun } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { formatMessage } from "../i18n/content";
import type { SiteContent } from "../i18n/types";

type Theme = "system" | "light" | "dark";

const themes: Theme[] = ["dark", "light", "system"];

interface ThemeToggleProps {
  content: SiteContent["theme"];
}

export function ThemeToggle({ content }: ThemeToggleProps) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("skills-theme");
    return themes.includes(saved as Theme) ? (saved as Theme) : "dark";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("skills-theme", theme);

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const syncThemeColor = () => {
      const isDark = theme === "dark" || (theme === "system" && media.matches);
      document
        .querySelector('meta[name="theme-color"]')
        ?.setAttribute("content", isDark ? "#000000" : "#f5f7fc");
    };

    syncThemeColor();
    if (theme !== "system") return;

    media.addEventListener("change", syncThemeColor);
    return () => media.removeEventListener("change", syncThemeColor);
  }, [theme]);

  const nextTheme = () => {
    const next = themes[(themes.indexOf(theme) + 1) % themes.length];
    setTheme(next);
  };

  const Icon = theme === "light" ? Sun : theme === "dark" ? Moon : Desktop;
  const label = content[theme];

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={nextTheme}
      aria-label={formatMessage(content.change, { theme: label })}
      title={formatMessage(content.title, { theme: label })}
    >
      <Icon size={18} weight="bold" aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </button>
  );
}
