import { Desktop, Moon, Sun } from "@phosphor-icons/react";
import { useEffect, useState } from "react";

type Theme = "system" | "light" | "dark";

const themes: Theme[] = ["dark", "light", "system"];
const labels: Record<Theme, string> = {
  system: "시스템",
  light: "라이트",
  dark: "다크",
};

export function ThemeToggle() {
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
        ?.setAttribute("content", isDark ? "#090a09" : "#f4f3ef");
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

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={nextTheme}
      aria-label={`현재 ${labels[theme]} 테마. 테마 변경`}
      title={`테마: ${labels[theme]}`}
    >
      <Icon size={18} weight="bold" aria-hidden="true" />
      <span>{labels[theme]}</span>
    </button>
  );
}
