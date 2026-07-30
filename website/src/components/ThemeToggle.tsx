import { Desktop, Moon, Sun } from "@phosphor-icons/react";
import { useEffect, useState } from "react";

type Theme = "system" | "light" | "dark";

const themes: Theme[] = ["system", "light", "dark"];
const labels: Record<Theme, string> = {
  system: "시스템",
  light: "라이트",
  dark: "다크",
};

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("skills-theme");
    return themes.includes(saved as Theme) ? (saved as Theme) : "system";
  });

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("skills-theme", theme);
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
