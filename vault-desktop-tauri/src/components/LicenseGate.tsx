import React, { useState } from "react";
import { Shield, Key, Mail, User, CheckCircle2, AlertCircle, ArrowRight, Loader2, Building } from "lucide-react";
import { invoke } from "@tauri-apps/api/core";

export interface LicenseInfo {
  license_key: string;
  role: "admin" | "user";
  company_name: string;
  tier: string;
  tier_display: string;
  setup_fee_gbp: number;
  per_user_monthly_gbp: number;
  max_seats: number;
  active_seats: number;
  admin_count: number;
  user_count: number;
  user_name: string;
  user_email: string;
  device_id: string;
  seat_id: string;
}

interface LicenseGateProps {
  onSuccess: (license: LicenseInfo) => void;
}

export const LicenseGate: React.FC<LicenseGateProps> = ({ onSuccess }) => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [licenseKey, setLicenseKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successLicense, setSuccessLicense] = useState<LicenseInfo | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!name.trim() || !email.trim() || !licenseKey.trim()) {
      setErrorMessage("Please complete all fields (Full Name, Work Email, License Key).");
      return;
    }

    setLoading(true);
    try {
      const result = await invoke<LicenseInfo>("verify_and_save_license", {
        licenseKey: licenseKey.trim(),
        name: name.trim(),
        email: email.trim(),
      });

      setSuccessLicense(result);
      setTimeout(() => {
        onSuccess(result);
      }, 1200);
    } catch (err: any) {
      console.error("License verification failed:", err);
      setErrorMessage(
        typeof err === "string" 
          ? err 
          : err?.message || "Invalid license key. Please check your key or contact support."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPreset = (key: string) => {
    setLicenseKey(key);
    setErrorMessage(null);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 text-white select-none">
      <div className="w-full max-w-md bg-neutral-900 border border-neutral-800 rounded-2xl shadow-2xl p-8 relative overflow-hidden">
        {/* Subtle decorative background accent */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-white/5 rounded-full blur-3xl pointer-events-none" />
        
        {/* Header */}
        <div className="flex flex-col items-center text-center mb-6">
          <div className="w-14 h-14 bg-neutral-800 border border-neutral-700 rounded-2xl flex items-center justify-center mb-4 shadow-inner">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-xl font-semibold tracking-tight text-white">
            SentraVault Activation
          </h1>
          <p className="text-xs text-neutral-400 mt-1.5 max-w-xs">
            Enter your enterprise license credentials to activate this endpoint.
          </p>
        </div>

        {/* Success Splash */}
        {successLicense ? (
          <div className="flex flex-col items-center text-center py-6 animate-fade-in">
            <div className="w-12 h-12 bg-emerald-500/10 border border-emerald-500/30 rounded-full flex items-center justify-center mb-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
            </div>
            <h2 className="text-base font-medium text-white">License Verified</h2>
            <p className="text-xs text-neutral-400 mt-1">
              Welcome, <span className="text-white font-medium">{successLicense.user_name}</span> ({successLicense.company_name})
            </p>
            <div className="mt-3 inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-neutral-800 border border-neutral-700 text-xs text-neutral-300">
              <span className={`w-2 h-2 rounded-full ${successLicense.role === 'admin' ? 'bg-indigo-400' : 'bg-emerald-400'}`} />
              Role: {successLicense.role.toUpperCase()} • {successLicense.tier_display.split('(')[0].trim()}
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Error Banner */}
            {errorMessage && (
              <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-xl flex items-start gap-2.5 text-xs text-red-200">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Name input */}
            <div>
              <label className="block text-xs font-medium text-neutral-300 mb-1">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-neutral-500 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="text"
                  required
                  placeholder="e.g. Dr. Sarah Jenkins"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-neutral-600 focus:outline-none focus:border-white transition-colors"
                />
              </div>
            </div>

            {/* Email input */}
            <div>
              <label className="block text-xs font-medium text-neutral-300 mb-1">
                Work Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-neutral-500 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="email"
                  required
                  placeholder="e.g. s.jenkins@acmehealth.co.uk"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-neutral-600 focus:outline-none focus:border-white transition-colors"
                />
              </div>
            </div>

            {/* License Key input */}
            <div>
              <label className="block text-xs font-medium text-neutral-300 mb-1 flex items-center justify-between">
                <span>License Key</span>
                <span className="text-[10px] text-neutral-500 font-normal">Admin or User Key</span>
              </label>
              <div className="relative">
                <Key className="w-4 h-4 text-neutral-500 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type="text"
                  required
                  placeholder="e.g. SV-ADM-ACME-5527 or SV-USR-ACME-5527"
                  value={licenseKey}
                  onChange={(e) => setLicenseKey(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-xl pl-9 pr-3 py-2 text-xs font-mono text-white placeholder-neutral-600 focus:outline-none focus:border-white transition-colors uppercase"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-white text-black hover:bg-neutral-200 active:scale-[0.99] font-medium py-2.5 px-4 rounded-xl text-xs transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-black" />
                  <span>Verifying License with Blind Cloud...</span>
                </>
              ) : (
                <>
                  <span>Activate SentraVault</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>

            {/* Presets & Helper section for rapid evaluation */}
            <div className="pt-3 border-t border-neutral-800/80 mt-4">
              <div className="flex items-center gap-1.5 text-[11px] font-medium text-neutral-400 mb-2">
                <Building className="w-3.5 h-3.5" />
                <span>Quick Deployment Presets:</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[10px]">
                <button
                  type="button"
                  onClick={() => handleApplyPreset("SV-ADM-ACME-5527")}
                  className="p-2 bg-neutral-950 border border-neutral-800 rounded-lg text-left hover:border-neutral-700 transition text-neutral-300"
                >
                  <div className="font-semibold text-white">Acme (Admin)</div>
                  <div className="text-neutral-500 truncate">SV-ADM-ACME-5527</div>
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyPreset("SV-USR-ACME-5527")}
                  className="p-2 bg-neutral-950 border border-neutral-800 rounded-lg text-left hover:border-neutral-700 transition text-neutral-300"
                >
                  <div className="font-semibold text-white">Acme (User)</div>
                  <div className="text-neutral-500 truncate">SV-USR-ACME-5527</div>
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
