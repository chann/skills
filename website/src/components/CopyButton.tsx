import { Check, Copy, WarningCircle } from "@phosphor-icons/react";
import { useEffect, useState } from "react";

type CopyState = "idle" | "copied" | "error";

interface CopyButtonProps {
  value: string;
  label?: string;
  compact?: boolean;
}

export function CopyButton({
  value,
  label = "복사",
  compact = false,
}: CopyButtonProps) {
  const [state, setState] = useState<CopyState>("idle");

  useEffect(() => {
    if (state === "idle") return;
    const timeout = window.setTimeout(() => setState("idle"), 2200);
    return () => window.clearTimeout(timeout);
  }, [state]);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setState("copied");
    } catch {
      setState("error");
    }
  };

  const text =
    state === "copied" ? "복사됨" : state === "error" ? "복사 실패" : label;
  const Icon = state === "copied" ? Check : state === "error" ? WarningCircle : Copy;

  return (
    <button
      className={`copy-button${compact ? " copy-button--compact" : ""}`}
      type="button"
      onClick={copy}
      aria-label={`${value} ${text}`}
      data-state={state}
    >
      <Icon size={17} weight="bold" aria-hidden="true" />
      <span>{text}</span>
    </button>
  );
}
