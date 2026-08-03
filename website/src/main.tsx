import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { resolveDocumentLocale } from "./i18n/locales";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App locale={resolveDocumentLocale()} />
  </StrictMode>,
);
