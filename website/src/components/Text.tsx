import type { ReactNode } from "react";

/** One block per heading line, so each line balances on its own at any width. */
export function Lines({ lines }: { lines: readonly string[] }) {
  return (
    <>
      {lines.map((line) => (
        <span key={line}>{line}</span>
      ))}
    </>
  );
}

/** Keep a flag such as `--quiz` on one line; browsers otherwise break after the dashes. */
export function withFlags(text: string): ReactNode[] {
  return text.split(/(--[a-z][a-z-]*)/).map((part, index) =>
    index % 2 ? (
      <span className="flag" key={index}>
        {part}
      </span>
    ) : (
      part
    ),
  );
}
