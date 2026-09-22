import React, { useState, useEffect, useMemo } from "react";
import { 
  Building2, 
  Users, 
  ShieldCheck, 
  CreditCard, 
  RefreshCcw, 
  Search, 
  UserX, 
  CheckCircle2, 
  AlertCircle, 
  HardDrive, 
  Laptop, 
  Clock, 
  Copy, 
  Check, 
  UserCheck,
  ShieldAlert
} from "lucide-react";
import { invoke } from "@tauri-apps/api/core";
import { LicenseInfo } from "./LicenseGate";

export interface DashboardSeat {
  id: string;
  role: "admin" | "user";
  name: string;
  email: string;
  device_id: string;
  device_os: string;
  status: "active" | "revoked";
  storage_used_str: string;
  storage_bytes: number;
  last_active: string;
  created_at: string;
}

export interface AdminDashboardOverview {
  company_name: string;
  tier: string;
  tier_display: string;
  setup_fee_gbp: number;
  per_user_monthly_gbp: number;
  monthly_run_rate_gbp: number;
  max_seats: number;
  total_active_seats: number;
  admin_count: number;
  user_count: number;
  remaining_seats: number;
  seats: DashboardSeat[];
}

interface EnterpriseAdminDashboardProps {
  licenseInfo: LicenseInfo | null;
}

export const EnterpriseAdminDashboard: React.FC<EnterpriseAdminDashboardProps> = ({ licenseInfo }) => {
  const [data, setData] = useState<AdminDashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "revoked">("all");
  const [roleFilter, setRoleFilter] = useState<"all" | "admin" | "user">("all");
  const [revokingSeatId, setRevokingSeatId] = useState<string | null>(null);
  const [seatToConfirmRevoke, setSeatToConfirmRevoke] = useState<DashboardSeat | null>(null);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);
  const [copiedKey, setCopiedKey] = useState(false);

  const fetchOverview = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    setError(null);
    try {
      const result = await invoke<AdminDashboardOverview>("fetch_admin_dashboard");
      setData(result);
    } catch (err: any) {
      console.error("Failed to load admin overview:", err);
      setError(typeof err === "string" ? err : err?.message || "Failed to load admin overview");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  const handleRevokeSeat = async (seat: DashboardSeat) => {
    setRevokingSeatId(seat.id);
    setActionSuccessMessage(null);
    try {
      await invoke("revoke_user_seat", { seatId: seat.id });
      setActionSuccessMessage(`Access for ${seat.name} (${seat.email}) has been revoked.`);
      setSeatToConfirmRevoke(null);
      await fetchOverview();
    } catch (err: any) {
      setError(typeof err === "string" ? err : err?.message || "Failed to revoke seat");
    } finally {
      setRevokingSeatId(null);
    }
  };

  const handleCopyLicenseKey = () => {
    if (!licenseInfo?.license_key) return;
    navigator.clipboard.writeText(licenseInfo.license_key);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2000);
  };

  // Filtered seats
  const filteredSeats = useMemo(() => {
    if (!data?.seats) return [];
    return data.seats.filter((s) => {
      const matchesSearch = 
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.device_id.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = statusFilter === "all" || s.status === statusFilter;
      const matchesRole = roleFilter === "all" || s.role === roleFilter;

      return matchesSearch && matchesStatus && matchesRole;
    });
  }, [data, searchQuery, statusFilter, roleFilter]);

  // Compute total storage across company
  const totalCompanyStorageStr = useMemo(() => {
    if (!data?.seats) return "0 MB";
    const totalBytes = data.seats.reduce((acc, s) => acc + (s.storage_bytes || 0), 0);
    if (totalBytes < 1024 * 1024) return `${(totalBytes / 1024).toFixed(1)} KB`;
    if (totalBytes < 1024 * 1024 * 1024) return `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(totalBytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
  }, [data]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4 animate-fade-in text-neutral-400">
        <div className="w-8 h-8 border-2 border-white/20 border-t-white rounded-full animate-spin" />
        <span className="text-xs font-mono tracking-wider uppercase text-neutral-500">Loading Enterprise Overview...</span>
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="max-w-xl mx-auto p-8 rounded-2xl bg-red-950/20 border border-red-800/40 text-center my-12">
        <ShieldAlert className="w-10 h-10 text-red-400 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-white mb-1">Administrative Access Required</h3>
        <p className="text-xs text-neutral-400 mb-6 max-w-md mx-auto">{error}</p>
        <button
          onClick={() => fetchOverview(true)}
          className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white rounded-xl text-xs font-medium transition cursor-pointer"
        >
          Try Again
        </button>
      </div>
    );
  }

  const activeSeats = data?.total_active_seats ?? 0;
  const maxSeats = data?.max_seats ?? 1;
  const seatPercentage = Math.min(100, Math.round((activeSeats / maxSeats) * 100));

  return (
    <div className="max-w-6xl space-y-6 pb-20 animate-in fade-in slide-in-from-bottom-2 duration-700">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-primary pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full bg-white/10 border border-white/15 text-[10px] font-semibold tracking-wider uppercase text-neutral-200">
              Enterprise Console
            </span>
            <span className="text-xs text-neutral-400 font-mono">•</span>
            <span className="text-xs text-neutral-300 font-medium">{data?.company_name}</span>
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            License & Seat Governance
          </h1>
          <p className="text-xs text-neutral-400 mt-0.5">
            Manage multi-user workstations, monitor live storage footprints, and revoke employee access.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchOverview(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-matte border border-border-primary hover:border-white/20 text-xs text-neutral-300 hover:text-white transition cursor-pointer disabled:opacity-50"
            title="Refresh allocation state"
          >
            <RefreshCcw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin text-white" : ""}`} />
            <span>Sync Stats</span>
          </button>

          {licenseInfo?.license_key && (
            <button
              onClick={handleCopyLicenseKey}
              className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white text-black hover:bg-neutral-200 text-xs font-medium transition cursor-pointer shadow-sm"
              title="Copy your admin license key"
            >
              {copiedKey ? <Check className="w-3.5 h-3.5 text-emerald-700" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copiedKey ? "Copied" : "Copy License Key"}</span>
            </button>
          )}
        </div>
      </div>

      {/* Success / Error notification toasts */}
      {actionSuccessMessage && (
        <div className="p-3.5 bg-emerald-950/30 border border-emerald-800/50 rounded-xl flex items-center justify-between text-xs text-emerald-300">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>{actionSuccessMessage}</span>
          </div>
          <button
            onClick={() => setActionSuccessMessage(null)}
            className="text-neutral-400 hover:text-white text-[10px] ml-4 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-red-950/40 border border-red-800/60 rounded-xl flex items-center justify-between text-xs text-red-200">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-neutral-400 hover:text-white text-[10px] ml-4 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Seat Allocation Meter */}
        <div className="p-5 rounded-2xl bg-matte border border-border-primary flex flex-col justify-between relative overflow-hidden group">
          <div>
            <div className="flex items-center justify-between text-neutral-400 mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Seats Allocated</span>
              <Users className="w-4 h-4 text-neutral-400" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-white tracking-tight">{activeSeats}</span>
              <span className="text-sm font-medium text-neutral-500">/ {maxSeats} Max</span>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-neutral-800 rounded-full h-2 mt-3 overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${
                  activeSeats >= maxSeats ? 'bg-amber-400' : 'bg-white'
                }`}
                style={{ width: `${seatPercentage}%` }}
              />
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border-primary/60 flex items-center justify-between text-[11px] text-neutral-400">
            <span>{data?.admin_count ?? 0} Admins • {data?.user_count ?? 0} Users</span>
            <span className={`font-semibold ${data?.remaining_seats === 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {data?.remaining_seats ?? 0} Available
            </span>
          </div>
        </div>

        {/* Card 2: Commercial Tier & Setup */}
        <div className="p-5 rounded-2xl bg-matte border border-border-primary flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-neutral-400 mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Plan & License</span>
              <Building2 className="w-4 h-4 text-neutral-400" />
            </div>
            <div className="text-lg font-bold text-white truncate mb-1">
              {data?.tier_display?.split("(")[0]?.trim() || "Enterprise"}
            </div>
            <p className="text-xs text-neutral-400">
              {data?.tier_display?.includes("(") ? `(${data.tier_display.split("(")[1]}` : "Multi-Seat Vault"}
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-border-primary/60 flex items-center justify-between text-[11px] text-neutral-400">
            <span>One-Time Setup</span>
            <span className="font-semibold text-white">
              £{data?.setup_fee_gbp?.toLocaleString("en-GB", { minimumFractionDigits: 2 })}
            </span>
          </div>
        </div>

        {/* Card 3: Monthly Billing Rate */}
        <div className="p-5 rounded-2xl bg-matte border border-border-primary flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-neutral-400 mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Subscription Run-Rate</span>
              <CreditCard className="w-4 h-4 text-neutral-400" />
            </div>
            <div className="flex items-baseline gap-1.5">
              <span className="text-3xl font-bold text-white tracking-tight">
                £{(data?.monthly_run_rate_gbp ?? 0).toFixed(2)}
              </span>
              <span className="text-xs font-normal text-neutral-400">/ mo</span>
            </div>
            <p className="text-xs text-neutral-500 mt-1">
              £{(data?.per_user_monthly_gbp ?? 0).toFixed(2)} per active user / mo
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-border-primary/60 flex items-center justify-between text-[11px] text-neutral-400">
            <span>Billing Cycle</span>
            <span className="text-neutral-300 font-medium">Monthly Post-Paid</span>
          </div>
        </div>

        {/* Card 4: Collective Cloud Vault Storage */}
        <div className="p-5 rounded-2xl bg-matte border border-border-primary flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-neutral-400 mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Encrypted Footprint</span>
              <HardDrive className="w-4 h-4 text-neutral-400" />
            </div>
            <div className="text-3xl font-bold text-white tracking-tight">
              {totalCompanyStorageStr}
            </div>
            <p className="text-xs text-neutral-400 mt-1">
              Across {data?.seats.length || 0} registered workstations
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-border-primary/60 flex items-center justify-between text-[11px] text-neutral-400">
            <span>Zero-Knowledge Relay</span>
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> Encrypted
            </span>
          </div>
        </div>
      </div>

      {/* Seat Governance Section */}
      <div className="p-6 rounded-2xl bg-matte border border-border-primary">
        {/* Table Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div>
            <h2 className="text-base font-semibold text-white">Registered Seats</h2>
            <p className="text-xs text-neutral-400 mt-0.5">
              Admins and users holding authenticated endpoint licenses.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 w-full sm:w-auto">
            {/* Search input */}
            <div className="relative min-w-[200px] flex-1 sm:flex-initial">
              <Search className="w-3.5 h-3.5 text-neutral-500 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                placeholder="Search user or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-white transition-colors"
              />
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="bg-neutral-950 border border-neutral-800 rounded-xl px-2.5 py-1.5 text-xs text-neutral-300 focus:outline-none focus:border-white cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active Only</option>
              <option value="revoked">Revoked Only</option>
            </select>

            {/* Role Filter */}
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value as any)}
              className="bg-neutral-950 border border-neutral-800 rounded-xl px-2.5 py-1.5 text-xs text-neutral-300 focus:outline-none focus:border-white cursor-pointer"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admins</option>
              <option value="user">Standard Users</option>
            </select>
          </div>
        </div>

        {/* Seat Table */}
        <div className="overflow-x-auto rounded-xl border border-border-primary/80">
          <table className="w-full text-left text-xs text-neutral-300">
            <thead className="bg-neutral-950/60 border-b border-border-primary/80 text-[11px] font-semibold text-neutral-400 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">User & Work Email</th>
                <th className="py-3 px-4">Role</th>
                <th className="py-3 px-4">Device & OS</th>
                <th className="py-3 px-4">Storage Used</th>
                <th className="py-3 px-4">Last Active</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-primary/60">
              {filteredSeats.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-neutral-500">
                    No seats match the current filter criteria.
                  </td>
                </tr>
              ) : (
                filteredSeats.map((seat) => {
                  const isCurrentSessionUser = licenseInfo?.seat_id === seat.id;
                  const isActive = seat.status === "active";
                  const isAdmin = seat.role === "admin";

                  return (
                    <tr key={seat.id} className="hover:bg-white/[0.02] transition-colors">
                      {/* Name & Email */}
                      <td className="py-3 px-4">
                        <div className="font-medium text-white flex items-center gap-1.5">
                          <span>{seat.name}</span>
                          {isCurrentSessionUser && (
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-neutral-800 text-neutral-400 border border-neutral-700">
                              You
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-neutral-400 font-mono">{seat.email}</div>
                      </td>

                      {/* Role */}
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold uppercase tracking-wider ${
                          isAdmin 
                            ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' 
                            : 'bg-neutral-800 text-neutral-300 border border-neutral-700'
                        }`}>
                          {isAdmin ? <ShieldCheck className="w-3 h-3" /> : <UserCheck className="w-3 h-3" />}
                          {seat.role}
                        </span>
                      </td>

                      {/* Device & OS */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1.5 text-neutral-300">
                          <Laptop className="w-3.5 h-3.5 text-neutral-500 shrink-0" />
                          <span className="truncate max-w-[130px]" title={seat.device_id}>
                            {seat.device_id || "Workstation"}
                          </span>
                        </div>
                        <div className="text-[10px] text-neutral-500">{seat.device_os || "Windows"}</div>
                      </td>

                      {/* Storage */}
                      <td className="py-3 px-4 font-mono text-neutral-300">
                        {seat.storage_used_str || "0 B"}
                      </td>

                      {/* Last Active */}
                      <td className="py-3 px-4 text-neutral-400">
                        <div className="flex items-center gap-1 text-[11px]">
                          <Clock className="w-3 h-3 text-neutral-500" />
                          <span>{seat.last_active ? new Date(seat.last_active).toLocaleDateString() : seat.created_at}</span>
                        </div>
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                          isActive 
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-emerald-400' : 'bg-red-400'}`} />
                          {isActive ? 'Active' : 'Revoked'}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        {isActive ? (
                          <button
                            onClick={() => setSeatToConfirmRevoke(seat)}
                            disabled={isCurrentSessionUser || revokingSeatId === seat.id}
                            title={isCurrentSessionUser ? "You cannot revoke your active admin session" : "Revoke employee access"}
                            className="px-2.5 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-neutral-400 hover:text-red-400 hover:border-red-900/60 transition text-[11px] cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
                          >
                            {revokingSeatId === seat.id ? "Revoking..." : "Revoke"}
                          </button>
                        ) : (
                          <span className="text-[11px] text-neutral-600 italic">Revoked</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footnote / Guidance */}
        <div className="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between text-[11px] text-neutral-500 gap-2">
          <div>
            Note: Both Admin and Standard User activations count towards your total seat cap ({activeSeats}/{maxSeats}).
          </div>
          <div className="text-neutral-400">
            To provision more seats or upgrade tier, contact SentraVault enterprise support.
          </div>
        </div>
      </div>

      {/* Revocation Confirmation Modal */}
      {seatToConfirmRevoke && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fade-in">
          <div className="w-full max-w-sm bg-neutral-900 border border-neutral-800 rounded-2xl p-6 shadow-2xl">
            <div className="w-10 h-10 bg-red-950/40 border border-red-800/60 rounded-xl flex items-center justify-center mb-4 text-red-400">
              <UserX className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">Revoke Workstation Seat?</h3>
            <p className="text-xs text-neutral-400 mt-2 leading-relaxed">
              Are you sure you want to revoke the license seat for{" "}
              <strong className="text-white">{seatToConfirmRevoke.name}</strong> ({seatToConfirmRevoke.email})?
              Their desktop client will immediately be barred from mounting or unlocking the zero-knowledge vault.
            </p>
            <div className="flex items-center justify-end gap-3 mt-6">
              <button
                type="button"
                onClick={() => setSeatToConfirmRevoke(null)}
                disabled={revokingSeatId !== null}
                className="px-3.5 py-2 rounded-xl bg-neutral-800 text-neutral-300 hover:text-white text-xs font-medium transition cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleRevokeSeat(seatToConfirmRevoke)}
                disabled={revokingSeatId !== null}
                className="px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white text-xs font-medium transition cursor-pointer shadow-sm"
              >
                {revokingSeatId ? "Revoking Access..." : "Confirm Revocation"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
