import { useState, useMemo } from "react";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Building2, Loader2, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";
import { useLoginBranding } from "../hooks/useStoreSettings";
import { getAssetUrl } from "../services/storeSettings";

export default function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const { data: branding } = useLoginBranding();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const backgroundUrl = branding?.login_background_path
    ? getAssetUrl("/store-settings/login-background", branding.login_background_path)
    : null;
  const logoUrl = branding?.login_logo_path
    ? getAssetUrl("/store-settings/login-logo", branding.login_logo_path)
    : null;
  const welcomeTitle = branding?.login_title || t("storeSettings.loginDefaults.title");
  const welcomeSubtitle =
    branding?.login_subtitle || t("storeSettings.loginDefaults.subtitle");

  const schema = useMemo(() => z.object({
    email: z.string().min(1, t("auth.validation.emailRequired")).email(t("auth.validation.emailInvalid")),
    password: z.string().min(1, t("auth.validation.passwordRequired")),
  }), [t]);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) });

  const onSubmit = async (values) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
    } catch (err) {
      toast.error(err.response?.data?.message || t("auth.toast.loginFailed"));
    } finally {
      setLoading(false);
    }
  };

  const isRtl = document.documentElement.dir === "rtl";

  return (
    <div className="min-h-screen flex">
      {/* Left decorative panel */}
      <div className={`hidden lg:flex lg:w-1/2 xl:w-[55%] relative overflow-hidden ${backgroundUrl ? "bg-primary-900" : "bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900"}`}>
        {backgroundUrl ? (
          <img
            src={backgroundUrl}
            alt=""
            className="absolute inset-0 w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl" />
            <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl" />
            <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-primary-300 rounded-full blur-3xl" />
          </div>
        )}
        <div className="absolute inset-0 bg-primary-900/55" />
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-20 w-full">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white/15 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20">
              {logoUrl ? (
                <img src={logoUrl} alt={welcomeTitle} className="w-7 h-7 object-contain" />
              ) : (
                <Building2 className="w-7 h-7 text-white" />
              )}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">{welcomeTitle}</h2>
              <p className="text-xs text-primary-200 font-medium">{welcomeSubtitle}</p>
            </div>
          </div>
          <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-6">
            {t("auth.heroTitle")}
            <br />
            <span className="text-primary-200">{t("auth.heroTitleAccent")}</span>
          </h1>
          <p className="text-base text-primary-100/80 max-w-md leading-relaxed">
            {t("auth.heroDescription")}
          </p>
          <div className="flex gap-8 mt-12">
            {[
              { value: "6+", label: t("auth.stats.modules") },
              { value: "100%", label: t("auth.stats.secure") },
              { value: "24/7", label: t("auth.stats.available") },
            ].map(({ value, label }) => (
              <div key={label}>
                <p className="text-2xl font-bold text-white">{value}</p>
                <p className="text-xs text-primary-200/70 font-medium mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center px-6 sm:px-12 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile-only brand */}
          <div className="flex items-center gap-3 mb-10 lg:hidden">
            <div className="w-11 h-11 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-500/25">
              {logoUrl ? (
                <img src={logoUrl} alt={welcomeTitle} className="w-6 h-6 object-contain" />
              ) : (
                <Building2 className="w-6 h-6 text-white" />
              )}
            </div>
            <div className="min-w-0">
              <span className="block text-xl font-bold text-surface-900 tracking-tight truncate">{welcomeTitle}</span>
              <span className="block text-xs text-surface-400 truncate">{welcomeSubtitle}</span>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-surface-900 tracking-tight">{t("auth.welcomeBack")}</h2>
            <p className="text-sm text-surface-400 mt-1.5">{t("auth.signInSubtitle")}</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-[13px] font-semibold text-surface-700 mb-1.5">
                {t("auth.emailLabel")}
              </label>
              <div className="relative">
                <Mail className="absolute start-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  {...register("email")}
                  className={`w-full ps-11 pe-4 py-3 border rounded-xl text-sm text-surface-800 placeholder:text-surface-300 transition-all duration-150
                    focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
                    ${errors.email ? "border-red-300 bg-red-50/30" : "border-surface-200 bg-surface-50 hover:border-surface-300"}`}
                  placeholder={t("auth.emailPlaceholder")}
                />
              </div>
              {errors.email && (
                <p className="text-xs text-red-500 mt-1.5 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-[13px] font-semibold text-surface-700 mb-1.5">
                {t("auth.passwordLabel")}
              </label>
              <div className="relative">
                <Lock className="absolute start-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  {...register("password")}
                  className={`w-full ps-11 pe-12 py-3 border rounded-xl text-sm text-surface-800 placeholder:text-surface-300 transition-all duration-150
                    focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
                    ${errors.password ? "border-red-300 bg-red-50/30" : "border-surface-200 bg-surface-50 hover:border-surface-300"}`}
                  placeholder={t("auth.passwordPlaceholder")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute end-3.5 top-1/2 -translate-y-1/2 p-1 text-surface-400 hover:text-surface-600 transition-colors"
                  aria-label={showPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-500 mt-1.5 font-medium">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-sm font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-150 shadow-lg shadow-primary-600/25 hover:shadow-xl hover:shadow-primary-600/30 active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  {t("auth.signingIn")}
                </>
              ) : (
                <>
                  {t("auth.signIn")}
                  <ArrowRight className={`w-4 h-4 ${isRtl ? "rotate-180" : ""}`} />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-xs text-surface-400 mt-8">
            {t("auth.footer")}
          </p>
        </div>
      </div>
    </div>
  );
}
