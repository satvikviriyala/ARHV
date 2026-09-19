/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { port: 5173, strictPort: true },
  build: { sourcemap: false, chunkSizeWarningLimit: 1500 },
  test: { environment: "jsdom", globals: false, include: ["src/**/*.test.{ts,tsx}"] },
});
