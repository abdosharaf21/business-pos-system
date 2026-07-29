import { useTranslation } from "react-i18next";
import { Globe } from "lucide-react";

const languages = [
  { code: "en", labelKey: "language.english", dir: "ltr" },
  { code: "ar", labelKey: "language.arabic", dir: "rtl" },
];

export default function LanguageSwitcher() {
  const { t, i18n } = useTranslation();

  const handleChange = (e) => {
    const lang = e.target.value;
    i18n.changeLanguage(lang);
    localStorage.setItem("i18nextLng", lang);
    document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
  };

  return (
    <div className="flex items-center gap-2">
      <Globe className="w-4 h-4 text-surface-400 shrink-0" />
      <select
        value={i18n.language}
        onChange={handleChange}
        className="text-[12px] bg-transparent border border-surface-200 rounded-lg px-2 py-1.5 text-surface-600 font-medium focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:border-primary-500 cursor-pointer appearance-none"
      >
        {languages.map(({ code, labelKey }) => (
          <option key={code} value={code}>
            {t(labelKey)}
          </option>
        ))}
      </select>
    </div>
  );
}
