import { defineConfig } from "npm:vite@^5.0.0";
import react from "npm:@vitejs/plugin-react@^4.0.0";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
