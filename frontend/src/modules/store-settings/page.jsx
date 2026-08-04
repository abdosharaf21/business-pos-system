import { useState, useMemo, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { storeSettingsService } from "./api";
import { setStoreSettings, getAssetUrl } from "./cache";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import {
  Store,
  Phone,
  Briefcase,
  Receipt,
  Image as ImageIcon,
  Building2,
  Loader2,
  Save,
  Upload,
  Trash2,
} from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS =
  "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const ERROR_CLASS = "text-[11px] text-red-500 mt-1 font-medium";

const LOGIN_ALLOWED_MIME = ["image/png", "image/jpeg", "image/jpg", "image/webp"];
const LOGIN_ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "webp"];
const LOGIN_MAX_SIZE = 5 * 1024 * 1024;
const LOGO_MAX_SIZE = 2 * 1024 * 1024;

function buildSchema(t) {
  const required = (key) => t(key);
  return z.object({
    store_name: z
      .string()
      .min(1, required("storeSettings.validation.storeNameRequired"))
      .max(150),
    owner_name: z.string().max(150),
    phone: z
      .string()
      .max(20)
      .refine(
        (value) =>
          !value ||
          (/^[0-9+\-() ]+$/.test(value) && value.replace(/\D/g, "").length >= 7),
        required("storeSettings.validation.phoneInvalid")
      ),
    email: z
      .string()
      .max(150)
      .refine(
        (value) => !value || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        required("storeSettings.validation.emailInvalid")
      ),
    website: z.string().max(150),
    address: z.string().max(255),
    tax_number: z.string().max(50),
    currency: z
      .string()
      .min(1, required("storeSettings.validation.required"))
      .max(10),
    receipt_footer: z.string().max(500),
    login_title: z.string().max(150),
    login_subtitle: z.string().max(255),
  });
}

const SECTION_ICON = {
  general: Store,
  contact: Phone,
  business: Briefcase,
  receipt: Receipt,
  branding: ImageIcon,
  loginBranding: Building2,
};

function SettingsSection({ id, title, description, children }) {
  const Icon = SECTION_ICON[id];
  return (
    <section className="bg-white rounded-2xl border border-surface-200 shadow-sm overflow-hidden">
      <div className="flex items-start gap-3 px-6 py-4 border-b border-surface-100">
        <div className="w-9 h-9 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center shrink-0">
          <Icon className="w-[18px] h-[18px]" />
        </div>
        <div>
          <h2 className="text-[15px] font-bold text-surface-900">{title}</h2>
          {description && (
            <p className="text-[13px] text-surface-400 mt-0.5">{description}</p>
          )}
        </div>
      </div>
      <div className="p-6">{children}</div>
    </section>
  );
}

function Field({ label, error, children }) {
  return (
    <div>
      <label className={LABEL_CLASS}>{label}</label>
      {children}
      {error && <p className={ERROR_CLASS}>{error.message}</p>}
    </div>
  );
}

function ImageUploadField({
  label,
  hint,
  previewUrl,
  alt,
  accept,
  onSelectFile,
  onRemove,
  aspect = "square",
  fit = "contain",
}) {
  const { t } = useTranslation();
  const boxClass =
    aspect === "wide"
      ? "w-40 h-24"
      : "w-24 h-24";
  return (
    <div>
      <span className={LABEL_CLASS}>{label}</span>
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div
          className={`${boxClass} rounded-xl border-2 border-dashed border-surface-200 bg-surface-50 flex items-center justify-center overflow-hidden shrink-0`}
        >
          {previewUrl ? (
            <img
              src={previewUrl}
              alt={alt}
              className={`w-full h-full ${fit === "cover" ? "object-cover" : "object-contain"}`}
            />
          ) : (
            <ImageIcon className="w-8 h-8 text-surface-300" />
          )}
        </div>
        <div className="space-y-2">
          <label className="inline-flex items-center gap-2 px-4 py-2.5 border border-surface-200 bg-white text-[13px] font-semibold text-surface-700 rounded-xl hover:bg-surface-50 cursor-pointer transition-colors">
            <Upload className="w-4 h-4" />
            {t("storeSettings.uploadImage")}
            <input
              type="file"
              accept={accept}
              className="hidden"
              onChange={onSelectFile}
            />
          </label>
          {hint && <p className="text-[11px] text-surface-400">{hint}</p>}
          {previewUrl && (
            <button
              type="button"
              onClick={onRemove}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold text-red-600 bg-white border border-red-200 rounded-xl hover:bg-red-50 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              {t("storeSettings.removeImage")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function LoginPagePreview({ backgroundUrl, logoUrl, title, subtitle }) {
  const { t } = useTranslation();
  return (
    <div className="relative overflow-hidden rounded-xl border border-surface-200 shadow-sm bg-primary-900 min-h-[420px]">
      {backgroundUrl ? (
        <img
          src={backgroundUrl}
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900" />
      )}
      <div className="absolute inset-0 bg-primary-900/55" />
      <div className="relative z-10 h-full flex flex-col items-center justify-center text-center px-6 py-10">
        <div className="w-14 h-14 bg-white/15 backdrop-blur-sm rounded-2xl border border-white/20 flex items-center justify-center mb-4">
          {logoUrl ? (
            <img src={logoUrl} alt={title} className="w-8 h-8 object-contain" />
          ) : (
            <Building2 className="w-8 h-8 text-white" />
          )}
        </div>
        <h3 className="text-xl font-bold text-white tracking-tight break-words max-w-full">
          {title || t("storeSettings.loginDefaults.title")}
        </h3>
        <p className="text-xs text-primary-200 font-medium mt-1 break-words max-w-full">
          {subtitle || t("storeSettings.loginDefaults.subtitle")}
        </p>
        <div className="w-full max-w-[220px] mt-6 space-y-2">
          <div className="h-8 rounded-lg bg-white/10 border border-white/15" />
          <div className="h-8 rounded-lg bg-white/10 border border-white/15" />
          <div className="h-9 rounded-lg bg-white/90" />
        </div>
      </div>
    </div>
  );
}

export default function StoreSettingsPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [logoFile, setLogoFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [removeLogo, setRemoveLogo] = useState(false);
  const [loginBackgroundFile, setLoginBackgroundFile] = useState(null);
  const [loginBackgroundPreviewUrl, setLoginBackgroundPreviewUrl] = useState(null);
  const [removeLoginBackground, setRemoveLoginBackground] = useState(false);
  const [loginLogoFile, setLoginLogoFile] = useState(null);
  const [loginLogoPreviewUrl, setLoginLogoPreviewUrl] = useState(null);
  const [removeLoginLogo, setRemoveLoginLogo] = useState(false);

  const { data: settings, isLoading, error, refetch } = useQuery({
    queryKey: ["store-settings"],
    queryFn: async () => {
      const res = await storeSettingsService.get();
      return res.data.data;
    },
  });

  const schema = useMemo(() => buildSchema(t), [t]);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    values: settings
      ? {
          store_name: settings.store_name || "",
          owner_name: settings.owner_name || "",
          phone: settings.phone || "",
          email: settings.email || "",
          website: settings.website || "",
          address: settings.address || "",
          tax_number: settings.tax_number || "",
          currency: settings.currency || "EGP",
          receipt_footer: settings.receipt_footer || "",
          login_title: settings.login_title || "",
          login_subtitle: settings.login_subtitle || "",
        }
      : undefined,
  });

  const watchedLoginTitle = watch("login_title") || "";
  const watchedLoginSubtitle = watch("login_subtitle") || "";

  useEffect(() => {
    if (!settings) return;
    setPreviewUrl(settings.logo_path ? getAssetUrl("/store-settings/logo") : null);
    setLoginBackgroundPreviewUrl(
      settings.login_background_path
        ? getAssetUrl("/store-settings/login-background")
        : null
    );
    setLoginLogoPreviewUrl(
      settings.login_logo_path ? getAssetUrl("/store-settings/login-logo") : null
    );
  }, [settings]);

  const saveMutation = useMutation({
    mutationFn: (data) => {
      const files = {
        logo: logoFile,
        loginBackground: loginBackgroundFile,
        loginLogo: loginLogoFile,
      };
      const removes = {
        logo: removeLogo,
        loginBackground: removeLoginBackground,
        loginLogo: removeLoginLogo,
      };
      const hasFiles = Object.values(files).some(Boolean);
      const hasRemoves = Object.values(removes).some(Boolean);
      if (hasFiles || hasRemoves) {
        return storeSettingsService.updateWithFiles(data, files, removes);
      }
      return storeSettingsService.update(data);
    },
    onSuccess: (res) => {
      const updated = res.data.data;
      setStoreSettings(updated);
      queryClient.invalidateQueries({ queryKey: ["store-settings"] });
      setLogoFile(null);
      setLoginBackgroundFile(null);
      setLoginLogoFile(null);
      setRemoveLogo(false);
      setRemoveLoginBackground(false);
      setRemoveLoginLogo(false);
      setPreviewUrl(
        updated.logo_path ? getAssetUrl("/store-settings/logo") : null
      );
      setLoginBackgroundPreviewUrl(
        updated.login_background_path
          ? getAssetUrl("/store-settings/login-background")
          : null
      );
      setLoginLogoPreviewUrl(
        updated.login_logo_path ? getAssetUrl("/store-settings/login-logo") : null
      );
      toast.success(t("storeSettings.toast.saved"));
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("storeSettings.toast.saveFailed")),
  });

  const handleLogoChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      toast.error(t("storeSettings.toast.logoType"));
      return;
    }
    if (file.size > LOGO_MAX_SIZE) {
      toast.error(t("storeSettings.toast.logoSize"));
      return;
    }
    setRemoveLogo(false);
    setLogoFile(file);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const handleRemoveLogo = () => {
    setLogoFile(null);
    setRemoveLogo(true);
    setPreviewUrl(null);
  };

  const handleLoginImageChange = (event, kind) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const extension = (file.name.split(".").pop() || "").toLowerCase();
    const valid =
      LOGIN_ALLOWED_MIME.includes(file.type) ||
      LOGIN_ALLOWED_EXTENSIONS.includes(extension);
    if (!valid) {
      toast.error(t("storeSettings.toast.loginImageType"));
      return;
    }
    if (file.size > LOGIN_MAX_SIZE) {
      toast.error(t("storeSettings.toast.loginImageSize"));
      return;
    }
    if (kind === "loginBackground") {
      setRemoveLoginBackground(false);
      setLoginBackgroundFile(file);
      setLoginBackgroundPreviewUrl(URL.createObjectURL(file));
    } else {
      setRemoveLoginLogo(false);
      setLoginLogoFile(file);
      setLoginLogoPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleRemoveLoginBackground = () => {
    setLoginBackgroundFile(null);
    setRemoveLoginBackground(true);
    setLoginBackgroundPreviewUrl(null);
  };

  const handleRemoveLoginLogo = () => {
    setLoginLogoFile(null);
    setRemoveLoginLogo(true);
    setLoginLogoPreviewUrl(null);
  };

  const onSubmit = (data) => {
    saveMutation.mutate(data);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error)
    return (
      <ErrorDisplay
        message={error.response?.data?.message || error.message}
        onRetry={refetch}
      />
    );

  return (
    <div>
      <PageHeader
        title={t("storeSettings.title")}
        description={t("storeSettings.subtitle")}
        actions={
          <button
            onClick={handleSubmit(onSubmit)}
            disabled={saveMutation.isPending}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20 disabled:opacity-60"
          >
            {saveMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            {t("storeSettings.save")}
          </button>
        }
      />

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 max-w-4xl">
        <SettingsSection
          id="general"
          title={t("storeSettings.sections.general.title")}
          description={t("storeSettings.sections.general.description")}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Field
              label={t("storeSettings.fields.storeName")}
              error={errors.store_name}
            >
              <input
                {...register("store_name")}
                placeholder={t("storeSettings.placeholders.storeName")}
                className={INPUT_CLASS}
              />
            </Field>
            <Field
              label={t("storeSettings.fields.ownerName")}
              error={errors.owner_name}
            >
              <input
                {...register("owner_name")}
                placeholder={t("storeSettings.placeholders.ownerName")}
                className={INPUT_CLASS}
              />
            </Field>
          </div>
        </SettingsSection>

        <SettingsSection
          id="contact"
          title={t("storeSettings.sections.contact.title")}
          description={t("storeSettings.sections.contact.description")}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Field label={t("storeSettings.fields.phone")} error={errors.phone}>
              <input
                {...register("phone")}
                placeholder={t("storeSettings.placeholders.phone")}
                dir="ltr"
                className={INPUT_CLASS}
              />
            </Field>
            <Field label={t("storeSettings.fields.email")} error={errors.email}>
              <input
                {...register("email")}
                placeholder={t("storeSettings.placeholders.email")}
                dir="ltr"
                className={INPUT_CLASS}
              />
            </Field>
            <Field
              label={t("storeSettings.fields.website")}
              error={errors.website}
            >
              <input
                {...register("website")}
                placeholder={t("storeSettings.placeholders.website")}
                dir="ltr"
                className={INPUT_CLASS}
              />
            </Field>
            <Field
              label={t("storeSettings.fields.address")}
              error={errors.address}
            >
              <input
                {...register("address")}
                placeholder={t("storeSettings.placeholders.address")}
                className={INPUT_CLASS}
              />
            </Field>
          </div>
        </SettingsSection>

        <SettingsSection
          id="business"
          title={t("storeSettings.sections.business.title")}
          description={t("storeSettings.sections.business.description")}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <Field
              label={t("storeSettings.fields.taxNumber")}
              error={errors.tax_number}
            >
              <input
                {...register("tax_number")}
                placeholder={t("storeSettings.placeholders.taxNumber")}
                className={INPUT_CLASS}
              />
            </Field>
            <Field
              label={t("storeSettings.fields.currency")}
              error={errors.currency}
            >
              <select {...register("currency")} className={INPUT_CLASS}>
                {["EGP", "USD", "EUR", "GBP", "SAR", "AED", "KWD", "QAR", "JOD", "TRY"].map(
                  (code) => (
                    <option key={code} value={code}>
                      {code}
                    </option>
                  )
                )}
              </select>
            </Field>
          </div>
        </SettingsSection>

        <SettingsSection
          id="receipt"
          title={t("storeSettings.sections.receipt.title")}
          description={t("storeSettings.sections.receipt.description")}
        >
          <Field
            label={t("storeSettings.fields.receiptFooter")}
            error={errors.receipt_footer}
          >
            <textarea
              {...register("receipt_footer")}
              rows={3}
              placeholder={t("storeSettings.placeholders.receiptFooter")}
              className={`${INPUT_CLASS} resize-none`}
            />
          </Field>
        </SettingsSection>

        <SettingsSection
          id="branding"
          title={t("storeSettings.sections.branding.title")}
          description={t("storeSettings.sections.branding.description")}
        >
          <ImageUploadField
            label={t("storeSettings.fields.storeLogo")}
            hint={t("storeSettings.hints.logo")}
            previewUrl={previewUrl}
            alt={t("storeSettings.logoPreviewAlt")}
            accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
            aspect="square"
            fit="contain"
            onSelectFile={handleLogoChange}
            onRemove={handleRemoveLogo}
          />
        </SettingsSection>

        <SettingsSection
          id="loginBranding"
          title={t("storeSettings.sections.loginBranding.title")}
          description={t("storeSettings.sections.loginBranding.description")}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <Field
                  label={t("storeSettings.fields.loginTitle")}
                  error={errors.login_title}
                >
                  <input
                    {...register("login_title")}
                    placeholder={t("storeSettings.placeholders.loginTitle")}
                    className={INPUT_CLASS}
                  />
                </Field>
                <Field
                  label={t("storeSettings.fields.loginSubtitle")}
                  error={errors.login_subtitle}
                >
                  <input
                    {...register("login_subtitle")}
                    placeholder={t("storeSettings.placeholders.loginSubtitle")}
                    className={INPUT_CLASS}
                  />
                </Field>
              </div>
              <ImageUploadField
                label={t("storeSettings.fields.loginBackground")}
                hint={t("storeSettings.hints.loginImage")}
                previewUrl={loginBackgroundPreviewUrl}
                alt={t("storeSettings.loginBackgroundPreviewAlt")}
                accept="image/png,image/jpeg,image/webp"
                aspect="wide"
                fit="cover"
                onSelectFile={(e) => handleLoginImageChange(e, "loginBackground")}
                onRemove={handleRemoveLoginBackground}
              />
              <ImageUploadField
                label={t("storeSettings.fields.loginLogo")}
                hint={t("storeSettings.hints.loginImage")}
                previewUrl={loginLogoPreviewUrl}
                alt={t("storeSettings.loginLogoPreviewAlt")}
                accept="image/png,image/jpeg,image/webp"
                aspect="square"
                fit="contain"
                onSelectFile={(e) => handleLoginImageChange(e, "loginLogo")}
                onRemove={handleRemoveLoginLogo}
              />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-700 mb-1">
                {t("storeSettings.loginPreview.title")}
              </p>
              <p className="text-[12px] text-surface-400 mb-3">
                {t("storeSettings.loginPreview.description")}
              </p>
              <LoginPagePreview
                backgroundUrl={loginBackgroundPreviewUrl}
                logoUrl={loginLogoPreviewUrl}
                title={watchedLoginTitle}
                subtitle={watchedLoginSubtitle}
              />
            </div>
          </div>
        </SettingsSection>
      </form>
    </div>
  );
}
