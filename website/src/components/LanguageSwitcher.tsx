import { useEffect, useRef, useState } from "react";
import { formatMessage } from "../i18n/content";
import { localeHref, localeRegistry } from "../i18n/locales";
import type { Locale, SiteContent } from "../i18n/types";

interface LanguageSwitcherProps {
  locale: Locale;
  labels: SiteContent["language"];
}

export function LanguageSwitcher({ locale, labels }: LanguageSwitcherProps) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || !open) return;
      setOpen(false);
      triggerRef.current?.focus();
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const hash = typeof window === "undefined" ? "" : window.location.hash;
  const current = localeRegistry[locale];
  const entries = Object.entries(localeRegistry) as Array<
    [Locale, (typeof localeRegistry)[Locale]]
  >;

  return (
    <div className="language-switcher" ref={rootRef}>
      <button
        ref={triggerRef}
        type="button"
        className="language-switcher__trigger"
        aria-expanded={open}
        aria-controls="language-navigation"
        aria-label={formatMessage(labels.trigger, { language: current.label })}
        onClick={() => setOpen((value) => !value)}
      >
        <span>{current.code}</span>
        <span aria-hidden="true">⌄</span>
      </button>
      {open ? (
        <nav
          id="language-navigation"
          className="language-switcher__menu"
          aria-label={labels.navigation}
        >
          <ul>
            {entries.map(([targetLocale, target]) => (
              <li key={targetLocale}>
                <a
                  href={localeHref(targetLocale, hash)}
                  aria-current={targetLocale === locale ? "page" : undefined}
                  onClick={() => setOpen(false)}
                >
                  {target.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
    </div>
  );
}
