import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Search, Command, CornerDownLeft, X } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { getVisibleModules, getVisibleSidebarGroups } from "../../layouts/navigationConfig";

export default function GlobalSearch() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [highlight, setHighlight] = useState(0);
  const inputRef = useRef(null);
  const panelRef = useRef(null);
  const isRtl = i18n.language === "ar";

  const items = [];
  for (const module of getVisibleModules(user?.role)) {
    items.push({
      key: module.to,
      labelKey: module.labelKey,
      to: module.to,
      icon: module.icon,
      group: module.labelKey,
    });
    const groups = getVisibleSidebarGroups(module.id, user?.role);
    for (const group of groups) {
      for (const item of group.items) {
        items.push({
          key: item.to,
          labelKey: item.labelKey,
          to: item.to,
          icon: item.icon,
          group: module.labelKey,
        });
      }
    }
  }

  const normalized = query.trim().toLowerCase();
  const filtered = normalized
    ? items.filter((item) => t(item.labelKey).toLowerCase().includes(normalized))
    : items;

  useEffect(() => {
    if (!open) return;
    setHighlight(0);
    const id = setTimeout(() => inputRef.current?.focus(), 0);
    return () => clearTimeout(id);
  }, [open, query]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!open) return;
    const handlePointerDown = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [open]);

  const close = () => {
    setOpen(false);
    setQuery("");
    setHighlight(0);
  };

  const go = (item) => {
    navigate(item.to);
    close();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      close();
      return;
    }
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(filtered.length - 1, h + 1));
      return;
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(0, h - 1));
      return;
    }
    if (e.key === "Enter" && filtered[highlight]) {
      e.preventDefault();
      go(filtered[highlight]);
    }
  };

  const grouped = [];
  const seen = new Set();
  for (const item of filtered) {
    const groupLabel = t(item.group);
    if (!seen.has(groupLabel)) {
      seen.add(groupLabel);
      grouped.push({ groupLabel, items: [] });
    }
    grouped[grouped.length - 1].items.push(item);
  }

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2 w-40 lg:w-60 px-3 py-2 rounded-xl border border-surface-200 bg-surface-50 text-surface-400 hover:bg-surface-100 hover:text-surface-600 transition-colors text-start"
        aria-label={t("header.search.placeholder")}
        aria-expanded={open}
      >
        <Search className="w-4 h-4 shrink-0" />
        <span className="flex-1 text-[12px] font-medium truncate">{t("header.search.placeholder")}</span>
        <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-white border border-surface-200 text-[10px] font-semibold text-surface-400 shadow-sm">
          <Command className="w-2.5 h-2.5" />
          K
        </kbd>
      </button>

      {open && (
        <div className="absolute end-0 top-full mt-2 w-[min(24rem,calc(100vw-2rem))] rounded-2xl bg-white border border-surface-200 shadow-xl shadow-surface-900/10 overflow-hidden z-50 dark:bg-surface-900 dark:border-surface-800 animate-in-fast">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-surface-100 dark:border-surface-800">
            <Search className="w-4 h-4 text-surface-400 shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t("header.search.placeholder")}
              className="flex-1 bg-transparent text-[13px] text-surface-800 placeholder:text-surface-300 focus:outline-none dark:text-surface-100"
              aria-label={t("header.search.placeholder")}
            />
            <button
              onClick={close}
              className="p-1 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-lg transition-colors"
              aria-label={t("common.closeDialog")}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="max-h-[340px] overflow-y-auto scrollbar-thin py-1.5">
            {grouped.length === 0 ? (
              <div className="px-4 py-10 text-center">
                <p className="text-sm font-semibold text-surface-600 dark:text-surface-200">{t("header.search.noResults")}</p>
                <p className="text-xs text-surface-400 mt-1">{t("header.search.noResultsHint")}</p>
              </div>
            ) : (
              (() => {
                let flatIndex = 0;
                return grouped.map((group) => (
                  <div key={group.groupLabel} className="mb-1">
                    <p className="px-4 py-1.5 text-[10px] font-semibold text-surface-400 uppercase tracking-wider">
                      {group.groupLabel}
                    </p>
                    <div className="space-y-0.5">
                      {group.items.map((item) => {
                        const Icon = item.icon;
                        const itemIndex = flatIndex++;
                        const isHighlight = itemIndex === highlight;
                        return (
                          <button
                            key={item.key}
                            onClick={() => go(item)}
                            onMouseEnter={() => setHighlight(itemIndex)}
                            className={`flex items-center gap-3 w-full px-4 py-2.5 text-start transition-colors ${
                              isHighlight ? "bg-primary-50 text-primary-700" : "text-surface-600 hover:bg-surface-50"
                            }`}
                          >
                            <Icon
                              className={`w-[18px] h-[18px] shrink-0 ${isHighlight ? "text-primary-600" : "text-surface-400"}`}
                              strokeWidth={1.8}
                            />
                            <span className="flex-1 text-[13px] font-medium truncate">{t(item.labelKey)}</span>
                            {isHighlight && (
                              <CornerDownLeft className={`w-3.5 h-3.5 text-primary-400 ${isRtl ? "rotate-180" : ""}`} />
                            )}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ));
              })()
            )}
          </div>
        </div>
      )}
    </div>
  );
}
