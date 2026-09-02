import React, { useState } from 'react';
import { 
  ShieldAlert, ShieldCheck, Key, Database, Zap, UserCheck, Lock, AlertOctagon, CheckCircle2
} from 'lucide-react';

export default function AdminApp() {
  const [sessionIdentity] = useState({
    userEmail: 'admin-secops@apexcapital.internal',
    identityProvider: 'Cloudflare-Access-Okta',
    accessLevel: 'TIER_0_ROOT'
  });

  const [circuitBreakerActive, setCircuitBreakerActive] = useState(false);
  const [webAuthnPending, setWebAuthnPending] = useState(false);
  const [pendingAction, setPendingAction] = useState(null);
  const [attestationFmt, setAttestationFmt] = useState('packed');

  // Approved AAGUID Allowlist (Simulated from config/aaguid_whitelist.json)
  const [aaguidWhitelist] = useState([
    { name: 'YubiKey 5 Series', aaguid: '2fc0579f-6522-472c-8328-01f1d6450507', fmt: 'packed' },
    { name: 'Windows Hello TPM', aaguid: '08987058-cad2-4f8b-9188-d2188f6219e2', fmt: 'tpm' },
    { name: 'Apple Secure Enclave', aaguid: 'dd482d9f-2213-41a6-9818-4d5c95786196', fmt: 'apple' }
  ]);

  const [unredactedLogs, setUnredactedLogs] = useState([
    { 
      id: 'LOG-001', 
      timestamp: '2026-08-30 13:40:12', 
      actor: 'secops-lead@apexcapital.internal', 
      sourceIp: '10.0.4.15', 
      action: 'ATTESTATION_VERIFIED', 
      detail: 'Format: packed | AAGUID: 2fc0579f-6522-472c-8328-01f1d6450507 (YubiKey 5)',
      source: 'sandbox-mock',
      sha256: 'e3b0c44288fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    }
  ]);

  const initiateStepUpChallenge = (actionType) => {
    setPendingAction({ actionType });
    setWebAuthnPending(true);
  };

  const handleWebAuthnVerification = () => {
    const selectedAuthenticator = aaguidWhitelist.find(a => a.fmt === attestationFmt) || aaguidWhitelist[0];

    if (pendingAction?.actionType === 'TOGGLE_CIRCUIT_BREAKER') {
      const nextState = !circuitBreakerActive;
      setCircuitBreakerActive(nextState);

      const newLog = {
        id: `LOG-00${unredactedLogs.length + 1}`,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
        actor: sessionIdentity.userEmail,
        sourceIp: '10.0.4.15',
        action: nextState ? 'CIRCUIT_BREAKER_ENGAGED' : 'CIRCUIT_BREAKER_DISENGAGED',
        detail: `Attestation: ${selectedAuthenticator.fmt} | AAGUID: ${selectedAuthenticator.aaguid} (${selectedAuthenticator.name})`,
        source: 'sandbox-mock',
        sha256: '8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4'
      };
      setUnredactedLogs(prev => [newLog, ...prev]);
    }
    setWebAuthnPending(false);
    setPendingAction(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/90 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4 sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-rose-600/20 text-rose-400 rounded-xl border border-rose-500/30">
            <ShieldAlert size={22} />
          </div>
          <div>
            <h1 className="text-sm font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              Master Admin Control App
              <span className="text-[10px] bg-rose-950 text-rose-400 font-mono px-2 py-0.5 rounded border border-rose-800 font-bold">HARDENED TIER-0</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              Identity: <span className="text-slate-200">{sessionIdentity.userEmail}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono bg-indigo-950/80 text-indigo-300 px-2.5 py-1 rounded border border-indigo-800/60">
            source: sandbox-mock
          </span>
          <button 
            onClick={() => initiateStepUpChallenge('TOGGLE_CIRCUIT_BREAKER')}
            className={`px-4 py-2 rounded-xl text-xs font-mono font-bold border transition-all flex items-center gap-2 ${
              circuitBreakerActive 
                ? 'bg-rose-600 text-white border-rose-500 shadow-lg shadow-rose-600/30' 
                : 'bg-slate-900 text-rose-400 border-rose-500/30 hover:bg-rose-950/40'
            }`}
          >
            <Zap size={14} />
            {circuitBreakerActive ? 'CIRCUIT BREAKER: ENGAGED' : 'ENGAGE CIRCUIT BREAKER'}
          </button>
        </div>
      </header>

      {/* WebAuthn Attestation Step-Up Modal */}
      {webAuthnPending && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-md w-full flex flex-col gap-5 shadow-2xl">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl border border-indigo-500/20">
                <Key size={24} />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100 uppercase">WebAuthn Hardware Step-Up</h3>
                <p className="text-xs text-slate-400 font-mono">Direct Conveyance Attestation Challenge</p>
              </div>
            </div>

            <div className="flex flex-col gap-2 font-mono text-xs">
              <label className="text-slate-400 text-[10px]">SIMULATE ATTESTATION FORMAT (fmt)</label>
              <select 
                value={attestationFmt} 
                onChange={(e) => setAttestationFmt(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="packed">packed (YubiKey / Security Keys)</option>
                <option value="tpm">tpm (Windows Hello)</option>
                <option value="apple">apple (Touch ID / Face ID)</option>
                <option value="android-key">android-key (Hardware Key)</option>
                <option value="fido-u2f">fido-u2f (Legacy Keys)</option>
              </select>
            </div>

            <div className="flex gap-3">
              <button 
                onClick={() => setWebAuthnPending(false)}
                className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono text-xs py-2.5 rounded-xl border border-slate-700"
              >
                Cancel
              </button>
              <button 
                onClick={handleWebAuthnVerification}
                className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-bold py-2.5 rounded-xl flex items-center justify-center gap-2"
              >
                <ShieldCheck size={14} /> Verify & Execute
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto flex flex-col gap-6">
        
        {/* AAGUID Allowlist Status */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-xs font-mono font-bold text-slate-200 uppercase flex items-center gap-2">
              <Lock size={14} className="text-indigo-400" /> Active AAGUID Hardware Allowlist
            </span>
            <span className="text-[10px] font-mono text-slate-500">config/aaguid_whitelist.json</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs">
            {aaguidWhitelist.map(item => (
              <div key={item.aaguid} className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex flex-col gap-1">
                <span className="text-slate-200 font-bold">{item.name}</span>
                <span className="text-[10px] text-indigo-400">fmt: {item.fmt}</span>
                <span className="text-[9px] text-slate-500 truncate">{item.aaguid}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Audit Stream */}
        <section className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
          <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-slate-200 uppercase">Cryptographic Audit Chain (SHA-256)</span>
            <span className="text-[10px] font-mono text-slate-500">source: sandbox-mock</span>
          </div>
          <div className="p-6 overflow-x-auto bg-slate-950/60 font-mono text-xs">
            {unredactedLogs.map((log) => (
              <div key={log.id} className="p-3 bg-slate-900/60 rounded-xl border border-slate-800/80 mb-2 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400 font-bold">{log.id} • {log.action}</span>
                  <span className="text-[10px] text-emerald-400">{log.sourceIp}</span>
                </div>
                <p className="text-slate-300 text-[11px]">{log.detail}</p>
                <div className="flex items-center justify-between text-[9px] text-slate-500 mt-1">
                  <span>SHA256: {log.sha256}</span>
                  <span>source: {log.source}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
