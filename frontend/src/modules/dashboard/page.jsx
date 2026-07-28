import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "./api";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Users, Briefcase, FolderOpen, UserCog, TrendingUp } from "lucide-react";
import { Badge, statusBadge } from "../../shared/components/Badge";

export default function DashboardPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const res = await dashboardService.getStats();
      return res.data.data;
    },
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const hasData = data.total_clients > 0 || data.total_services > 0;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">Dashboard</h1>
        <p className="text-sm text-surface-400 mt-1">Overview of your business development</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Total Clients" value={data.total_clients} icon={Users} color="blue" />
        <StatCard label="Total Services" value={data.total_services} icon={Briefcase} color="green" />
        <StatCard label="Categories" value={data.total_categories} icon={FolderOpen} color="purple" />
        <StatCard label="Users" value={data.total_users} icon={UserCog} color="orange" />
      </div>

      {!hasData ? (
        <div className="bg-white rounded-2xl border border-surface-200/80 shadow-card">
          <EmptyState
            icon={TrendingUp}
            title="Welcome to BizDev"
            description="Your system is ready. Start by adding clients, services, and categories to see your business data here."
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Clients */}
          <div className="bg-white rounded-2xl border border-surface-200/80 shadow-card overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-surface-100">
              <div>
                <h2 className="text-[15px] font-bold text-surface-900">Recent Clients</h2>
                <p className="text-[11px] text-surface-400 mt-0.5">Latest client activity</p>
              </div>
              <div className="w-9 h-9 bg-primary-50 rounded-xl flex items-center justify-center ring-1 ring-primary-100">
                <Users className="w-4 h-4 text-primary-600" />
              </div>
            </div>
            <div className="p-2">
              {data.recent_clients?.length > 0 ? (
                <div className="divide-y divide-surface-50">
                  {data.recent_clients.map((c) => (
                    <div key={c.id} className="flex items-center justify-between p-4 hover:bg-surface-50/50 rounded-xl transition-colors">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-xl bg-surface-100 flex items-center justify-center text-[11px] font-bold text-surface-500 shrink-0">
                          {c.company_name?.charAt(0)?.toUpperCase() || "?"}
                        </div>
                        <div className="min-w-0">
                          <p className="text-[13px] font-semibold text-surface-800 truncate">{c.company_name}</p>
                          <p className="text-[11px] text-surface-400 truncate">{c.contact_person}</p>
                        </div>
                      </div>
                      <Badge variant={statusBadge(c.status)}>{c.status}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="px-6 py-8 text-center">
                  <p className="text-sm text-surface-400">No clients yet</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Services */}
          <div className="bg-white rounded-2xl border border-surface-200/80 shadow-card overflow-hidden">
            <div className="flex items-center justify-between px-6 py-5 border-b border-surface-100">
              <div>
                <h2 className="text-[15px] font-bold text-surface-900">Recent Services</h2>
                <p className="text-[11px] text-surface-400 mt-0.5">Latest service offerings</p>
              </div>
              <div className="w-9 h-9 bg-emerald-50 rounded-xl flex items-center justify-center ring-1 ring-emerald-100">
                <Briefcase className="w-4 h-4 text-emerald-600" />
              </div>
            </div>
            <div className="p-2">
              {data.recent_services?.length > 0 ? (
                <div className="divide-y divide-surface-50">
                  {data.recent_services.map((s) => (
                    <div key={s.id} className="flex items-center justify-between p-4 hover:bg-surface-50/50 rounded-xl transition-colors">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-xl bg-surface-100 flex items-center justify-center text-[11px] font-bold text-surface-500 shrink-0">
                          {s.name?.charAt(0)?.toUpperCase() || "?"}
                        </div>
                        <div className="min-w-0">
                          <p className="text-[13px] font-semibold text-surface-800 truncate">{s.name}</p>
                          <p className="text-[11px] text-surface-400 truncate">{s.description || "No description"}</p>
                        </div>
                      </div>
                      <Badge variant={statusBadge(s.status)}>{s.status}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="px-6 py-8 text-center">
                  <p className="text-sm text-surface-400">No services yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
