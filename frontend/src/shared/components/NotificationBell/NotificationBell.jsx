import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck, Inbox, X } from "lucide-react";
import { notificationService } from "../../../modules/notifications/api";

const TYPE_VARIANT = {
  low_stock: "bg-amber-50 text-amber-700",
  out_of_stock: "bg-red-50 text-red-700",
  expired: "bg-red-50 text-red-700",
  expiring_soon: "bg-amber-50 text-amber-700",
};

const PRIORITY_DOT = {
  critical: "bg-red-500",
  warning: "bg-amber-400",
};

export default function NotificationBell() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState("all");
  const panelRef = useRef(null);

  const unreadQuery = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: async () => {
      const res = await notificationService.getUnreadCount();
      return res.data.data.unread_count;
    },
    refetchInterval: 60000,
  });

  const listQuery = useQuery({
    queryKey: ["notifications", "list", filter],
    queryFn: async () => {
      const params = { limit: 50 };
      if (filter === "unread") params.unread_only = true;
      if (filter === "critical") params.priority = "critical";
      const res = await notificationService.getAll(params);
      return res.data.data;
    },
    enabled: open,
  });

  const notifications = listQuery.data ?? [];
  const unreadCount = unreadQuery.data ?? 0;

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["notifications"] });
  };

  useEffect(() => {
    if (!open) return;
    const handlePointerDown = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  const handleMarkAllRead = async () => {
    try {
      await notificationService.markAllAsRead();
      invalidate();
    } catch {
      // Keep the panel open; unread state stays as-is.
    }
  };

  const handleOpenNotification = async (notification) => {
    try {
      if (!notification.is_read) {
        await notificationService.markAsRead(notification.id);
      }
    } catch {
      // Navigation still happens even if marking read fails.
    }
    invalidate();
    setOpen(false);
    navigate(`/products?product=${notification.product_id}`);
  };

  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const formatTime = (value) => {
    if (!value) return "";
    try {
      return new Date(value).toLocaleString(locale, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  const formatExpiration = (value) => {
    if (!value) return "";
    try {
      return new Date(value + "T00:00:00").toLocaleDateString(locale, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return value;
    }
  };

  const filters = [
    { value: "all", label: t("notifications.filters.all") },
    { value: "unread", label: t("notifications.filters.unread") },
    { value: "critical", label: t("notifications.filters.critical") },
  ];

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="relative p-2 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-lg transition-colors"
        aria-label={t("common.notifications")}
        aria-expanded={open}
      >
        <Bell className="w-[18px] h-[18px]" />
        {unreadCount > 0 && (
          <span className="absolute top-0.5 end-0.5 min-w-[18px] h-[18px] px-1 flex items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute end-0 top-full mt-2 w-[360px] max-w-[calc(100vw-2rem)] rounded-xl bg-white border border-surface-200 shadow-xl shadow-surface-900/10 overflow-hidden z-50 dark:bg-surface-900 dark:border-surface-800">
          <div className="flex items-center justify-between px-4 py-3 border-b border-surface-100 dark:border-surface-800">
            <h3 className="text-sm font-bold text-surface-900 dark:text-surface-100">
              {t("notifications.title")}
            </h3>
            <div className="flex items-center gap-1">
              <button
                onClick={handleMarkAllRead}
                disabled={unreadCount === 0}
                className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-semibold text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-40 disabled:hover:bg-transparent"
              >
                <CheckCheck className="w-3.5 h-3.5" />
                {t("notifications.markAllRead")}
              </button>
              <button
                onClick={() => setOpen(false)}
                className="p-1.5 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-lg transition-colors"
                aria-label={t("common.closeDialog")}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex gap-1 px-4 py-2 border-b border-surface-100 dark:border-surface-800">
            {filters.map(({ value, label }) => (
              <button
                key={value}
                onClick={() => setFilter(value)}
                className={`px-3 py-1.5 text-[11px] font-semibold rounded-lg transition-colors ${
                  filter === value
                    ? "bg-primary-50 text-primary-700"
                    : "text-surface-500 hover:bg-surface-50 hover:text-surface-700"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="max-h-[340px] overflow-y-auto">
            {listQuery.isLoading ? (
              <div className="px-4 py-10 text-center text-sm text-surface-400">
                {t("notifications.loading")}
              </div>
            ) : notifications.length === 0 ? (
              <div className="px-4 py-10 flex flex-col items-center gap-2 text-center">
                <Inbox className="w-8 h-8 text-surface-200" />
                <p className="text-sm font-semibold text-surface-600">
                  {t("notifications.empty")}
                </p>
                <p className="text-xs text-surface-400">
                  {t("notifications.emptyDescription")}
                </p>
              </div>
            ) : (
              <ul className="divide-y divide-surface-100 dark:divide-surface-800">
                {notifications.map((notification) => {
                  const unread = !notification.is_read;
                  return (
                    <li key={notification.id}>
                      <button
                        onClick={() => handleOpenNotification(notification)}
                        className="w-full text-start px-4 py-3 hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors flex gap-3"
                      >
                        <span
                          className={`mt-1.5 w-2 h-2 rounded-full shrink-0 ${PRIORITY_DOT[notification.priority] || "bg-surface-300"}`}
                        />
                        <span className="flex-1 min-w-0">
                          <span className="flex items-center justify-between gap-2">
                            <span className="text-xs font-bold text-surface-800 dark:text-surface-100 truncate">
                              {notification.product_name}
                            </span>
                            {unread && (
                              <span className="shrink-0 w-1.5 h-1.5 rounded-full bg-primary-500" />
                            )}
                          </span>
                          <span className="block text-xs text-surface-500 dark:text-surface-400 mt-0.5">
                            {notification.notification_type === "low_stock" &&
                              t("notifications.message.low_stock", { quantity: notification.quantity })}
                            {notification.notification_type === "out_of_stock" &&
                              t("notifications.message.out_of_stock")}
                            {notification.notification_type === "expired" &&
                              t("notifications.message.expired", {
                                expirationDate: formatExpiration(notification.expiration_date),
                              })}
                            {notification.notification_type === "expiring_soon" &&
                              t("notifications.message.expiring_soon", {
                                expirationDate: formatExpiration(notification.expiration_date),
                              })}
                          </span>
                          <span className="flex items-center justify-between mt-1.5">
                            <span className={`text-[10px] font-medium uppercase tracking-wide px-2 py-0.5 rounded-full ${TYPE_VARIANT[notification.notification_type] || "bg-surface-100 text-surface-500"}`}>
                              {t(`notifications.types.${notification.notification_type}`)}
                            </span>
                            <span className="text-[10px] text-surface-300">
                              {formatTime(notification.created_at)}
                            </span>
                          </span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
