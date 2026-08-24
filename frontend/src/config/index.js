const apiUrl =
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "/api";

const config = {
  apiBaseUrl: apiUrl,
};

export default config;
