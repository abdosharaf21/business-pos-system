import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Building2, Loader2, Mail, Lock, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";

const schema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

export default function LoginPage() {
  const { login } = useAuth();
  const [loading, setLoading] = useState(false);

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
      toast.error(err.response?.data?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left decorative panel */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] relative bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-primary-300 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-20 w-full">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white/15 backdrop-blur-sm rounded-2xl flex items-center justify-center border border-white/20">
              <Building2 className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">BizDev</h2>
              <p className="text-xs text-primary-200 font-medium">Management System</p>
            </div>
          </div>
          <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight mb-6">
            Business Development
            <br />
            <span className="text-primary-200">Made Simple</span>
          </h1>
          <p className="text-base text-primary-100/80 max-w-md leading-relaxed">
            Manage your clients, services, and team — all from one professional dashboard built for growing businesses.
          </p>
          <div className="flex gap-8 mt-12">
            {[
              { value: "6+", label: "Modules" },
              { value: "100%", label: "Secure" },
              { value: "24/7", label: "Available" },
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
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-surface-900 tracking-tight">BizDev</span>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-bold text-surface-900 tracking-tight">Welcome back</h2>
            <p className="text-sm text-surface-400 mt-1.5">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-[13px] font-semibold text-surface-700 mb-1.5">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  {...register("email")}
                  className={`w-full pl-11 pr-4 py-3 border rounded-xl text-sm text-surface-800 placeholder:text-surface-300 transition-all duration-150
                    focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
                    ${errors.email ? "border-red-300 bg-red-50/30" : "border-surface-200 bg-surface-50 hover:border-surface-300"}`}
                  placeholder="you@company.com"
                />
              </div>
              {errors.email && (
                <p className="text-xs text-red-500 mt-1.5 font-medium">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-[13px] font-semibold text-surface-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  {...register("password")}
                  className={`w-full pl-11 pr-4 py-3 border rounded-xl text-sm text-surface-800 placeholder:text-surface-300 transition-all duration-150
                    focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
                    ${errors.password ? "border-red-300 bg-red-50/30" : "border-surface-200 bg-surface-50 hover:border-surface-300"}`}
                  placeholder="Enter your password"
                />
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
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-xs text-surface-400 mt-8">
            Business Development Management System
          </p>
        </div>
      </div>
    </div>
  );
}
