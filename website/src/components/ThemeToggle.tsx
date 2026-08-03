import { Moon, Sun } from "@phosphor-icons/react";
import { useEffect, useState } from "react";
import { formatMessage } from "../i18n/content";
import type { SiteContent } from "../i18n/types";

type Theme = "light" | "dark";

const themeStorageKey = "skills-theme";

function isTheme(value: string | null | undefined): value is Theme {
  return value === "light" || value === "dark";
}

function readStoredTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(themeStorageKey);
    return isTheme(stored) ? stored : null;
  } catch {
    return null;
  }
}

function preferredTheme(): Theme {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function initialTheme(): Theme {
  const documentTheme = document.documentElement.dataset.theme;
  return isTheme(documentTheme)
    ? documentTheme
    : readStoredTheme() ?? preferredTheme();
}

interface ThemeToggleProps {
  content: SiteContent["theme"];
}

export function ThemeToggle({ content }: ThemeToggleProps) {
  const [theme, setTheme] = useState<Theme>(initialTheme);
  const [followsSystem, setFollowsSystem] = useState(() => readStoredTheme() === null);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document
      .querySelector('meta[name="theme-color"]')
      ?.setAttribute("content", theme === "dark" ? "#000000" : "#f5f7fc");
  }, [theme]);

  useEffect(() => {
    if (!followsSystem) return;

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const syncWithSystem = () => setTheme(media.matches ? "dark" : "light");
    syncWithSystem();
    media.addEventListener("change", syncWithSystem);
    return () => media.removeEventListener("change", syncWithSystem);
  }, [followsSystem]);

  const nextTheme = () => {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setFollowsSystem(false);
    setTheme(next);
    try {
      localStorage.setItem(themeStorageKey, next);
    } catch {
      // The visible theme can still change when storage is unavailable.
    }
  };

  const Icon = theme === "light" ? Sun : Moon;
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
