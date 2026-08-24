import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { applyTheme, getActiveTheme } from "./shared/utils/theme";
import "./index.css";

applyTheme(getActiveTheme());

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
