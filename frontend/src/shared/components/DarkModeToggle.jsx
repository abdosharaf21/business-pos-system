import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Moon, Sun } from "lucide-react";
import { getActiveTheme, THEMES, toggleTheme } from "../utils/theme";

export default function DarkModeToggle() {
  const { t } = useTranslation();
  const [theme, setThemeState] = useState(getActiveTheme);
  const isDark = theme === THEMES.DARK;

  const handleToggle = () => {
    setThemeState(toggleTheme());
  };

  return (
    <button
      onClick={handleToggle}
      className="p-2 text-surface-500 hover:bg-surface-100 rounded-xl transition-colors dark:text-surface-400 dark:hover:bg-surface-800"
      aria-label={t("common.toggleTheme")}
      aria-pressed={isDark}
      title={t("common.toggleTheme")}
    >
      {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
    </button>
  );
}
