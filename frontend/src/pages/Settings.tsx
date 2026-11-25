import { useEffect, useState } from "react";
import { monitoringApi } from "../api/actions";

export default function SettingsPage() {
  const [s,setS]=useState<any>({interval_sec:30,enabled:true});
  const [msg,setMsg]=useState("");
  useEffect(()=>{ monitoringApi.settings().then(setS).catch(()=>{}); },[]);
  const save=async()=>{ await monitoringApi.updateSettings(s); setMsg("Saved"); setTimeout(()=>setMsg(""),1500); };
  return <div className="space-y-4 max-w-3xl"><h1 className="text-3xl font-semibold">Settings</h1>
    <div className="card p-4 space-y-3"><div className="font-medium">Continuous Monitoring (Simulated)</div>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={!!s.enabled} onChange={e=>setS({...s,enabled:e.target.checked})}/> Enable simulated monitoring</label>
      <label className="block"><span className="label">Interval (seconds)</span><input className="input" type="number" min={5} value={s.interval_sec} onChange={e=>setS({...s,interval_sec:Number(e.target.value)})}/></label>
      <button className="btn" onClick={save}>Save Settings</button>{msg && <span className="text-green-400 text-sm ml-2">{msg}</span>}
    </div>
    <div className="card p-4 text-sm text-slate-300 space-y-2"><div className="font-medium text-white">Safety & Testing Policy</div>
      <p>Only test websites you own or have explicit permission to test. External checks are safe, low-volume, and timeout-limited.</p>
      <p>No DoS, no destructive attacks, no target modification. Server/database/network/backend failure injection is performed in controlled simulation/inferred model.</p>
      <p>Generated patches are review-only and never auto-executed. Results clearly label simulated/inferred data.</p>
    </div>
  </div>;
}
