import { defineConfig } from "vite";
import { codecovVitePlugin } from "@codecov/vite-plugin";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    codecovVitePlugin({
      enableBundleAnalysis: process.env.CODECOV_TOKEN !== undefined,
      bundleName: "period-tracker",
      uploadToken: process.env.CODECOV_TOKEN,
    }),
  ],
});
