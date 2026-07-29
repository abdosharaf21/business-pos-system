import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const host = env.VITE_HOST || "0.0.0.0";
  const port = parseInt(env.VITE_PORT || "5174", 10);
  const proxyTarget = env.VITE_PROXY_TARGET;

  return {
    plugins: [react(), tailwindcss()],
    server: {
      host,
      port,
      proxy: proxyTarget
        ? {
            "/api": {
              target: proxyTarget,
              changeOrigin: true,
            },
          }
        : undefined,
    },
  };
});
