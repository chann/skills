import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/skills/",
  build: {
    rollupOptions: {
      input: { main: "index.html", new: "new/index.html" },
    },
  },
});
