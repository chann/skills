import { useEffect, useState, type PropsWithChildren } from "react";
import type { SiteContent } from "../i18n/types";

interface HeadingLinkProps extends PropsWithChildren {
  hash: string;
  content: SiteContent["copy"];
}

/** A heading that links to itself: a click moves the address to it and copies that address. */
export function HeadingLink({ hash, content, children }: HeadingLinkProps) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const timeout = window.setTimeout(() => setCopied(false), 2200);
    return () => window.clearTimeout(timeout);
  }, [copied]);

  const copy = () => {
    // The href still moves the address bar when the clipboard is unavailable.
    navigator.clipboard
      ?.writeText(new URL(hash, window.location.href).href)
      .then(() => setCopied(true), () => undefined);
  };

  return (
    <a className="heading-link" href={hash} title={content.link} onClick={copy}>
      {children}
      <span className="heading-link__status" role="status">
        {copied ? content.linkCopied : ""}
      </span>
    </a>
  );
}
