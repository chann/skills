import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { resolveDocumentLocale } from "../i18n/locales";
import { NewApp } from "./NewApp";
import "./new.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <NewApp locale={resolveDocumentLocale()} />
  </StrictMode>,
);
