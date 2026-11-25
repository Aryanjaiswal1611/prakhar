import { useEffect, useState } from "react";
import axios from "axios";
import { websiteTestApi } from "../api/actions";
import { API_TIMEOUT_MS } from "../api/client";
import type { WebsiteTestResult } from "../types";
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from "recharts";
import InfraGraph from "../components/graph/InfraGraph";

function ScoreRing({score}:{score:number}) {
  const color = score>=90?"#22c55e":score>=75?"#5b8cff":score>=50?"#f59e0b":score>=25?"#fb7185":"#ef4444";
  return <div className="relative w-44 h-44 rounded-full grid place-items-center" style={{background:`conic-gradient(${color} ${score*3.6}deg, #1e293b 0deg)`}}>
    <div className="w-36 h-36 rounded-full bg-panel grid place-items-center text-center"><div><div className="text-4xl font-bold">{score}</div><div className="text-xs text-slate-400">/ 100</div></div></div>
  </div>;
}

function getErrorMessage(e: unknown): string {
  if (axios.isAxiosError(e)) {
    if (e.code === "ECONNABORTED" || /timeout/i.test(e.message || "")) return "Website request timed out.";
    if (!e.response) return "Backend server is unavailable. Please start the backend.";
    const detail = e.response.data?.detail;
    if (typeof detail === "string" && detail) return detail;
    if (detail && typeof detail === "object" && typeof (detail as any).message === "string") return (detail as any).message;
    return `Request failed (${e.response.status}).`;
  }
  if (e instanceof Error) return e.message;
  return "Unexpected error while running resilience test.";
}

const COLORS = ["#22c55e","#f59e0b","#ef4444","#5b8cff","#a78bfa","#14b8a6"];

export default function TestingLab({onResult, latest, discovery, onDiscover, selectedUrl}:{onResult:(r:WebsiteTestResult)=>void; latest:WebsiteTestResult|null; discovery:any; onDiscover:(url:string)=>Promise<void>; selectedUrl:string}) {
  const [url,setUrl]=useState(selectedUrl || "https://example.com");
  const [apiEndpoint,setApiEndpoint]=useState("");
  const [mode,setMode]=useState("safe_external");
  const [loading,setLoading]=useState(false);
  const [err,setErr]=useState("");
  const [res,setRes]=useState<WebsiteTestResult|null>(latest);
  useEffect(()=>{ if(latest) setRes(latest); },[latest?.id]);
  useEffect(()=>{ if(selectedUrl) setUrl(selectedUrl); },[selectedUrl]);

  const run = async () => {
    const target = url.trim();
    if (!target) { setErr("Please enter a website URL."); return; }
    setLoading(true); setErr("");
    try {
      const r = await websiteTestApi.run({url: target, mode, include_api_endpoint: apiEndpoint.trim() || undefined});
      if (!r || typeof r.overall_score !== "number" || !Array.isArray(r.tests)) throw new Error("Invalid response from backend.");
      setRes(r); onResult(r);
    } catch(e: unknown) { setErr(getErrorMessage(e)); }
    finally { setLoading(false); }
  };

  const factorData = res ? Object.entries(res.factors || {}).map(([k,v]:any)=>({factor:k.replaceAll("_"," "), score:Number(v.score)||0, weight:Math.round((v.weight||0)*100)})) : [];
  const statusData = res ? [{name:"Passed",value:res.tests.filter((t:any)=>t.passed).length},{name:"Failed",value:res.tests.filter((t:any)=>!t.passed).length}] : [];
  const latencyData = res ? res.tests.filter((t:any)=>/elapsed_ms=([0-9.]+)/.test(t.detail||"")).map((t:any)=>({name:t.name.slice(0,18), ms:Number((t.detail.match(/elapsed_ms=([0-9.]+)/)||[])[1]||0)})).slice(0,8) : [];
  const infra = discovery?.nodes ? {id:0,name:`Discovered: ${discovery.url}`,description:discovery.summary||"",nodes:discovery.nodes,edges:discovery.edges} : null;

  return <div className="space-y-6">
    <div><h1 className="text-3xl font-semibold">Website Resilience Testing Lab</h1><p className="text-slate-400 mt-1">Safe, real checks with live visualizations and auto infrastructure discovery. No destructive attacks.</p></div>
    <div className="card p-5 grid lg:grid-cols-[1fr_320px] gap-4">
      <div className="space-y-3">
        <label className="block"><span className="label">Website URL (test only sites you own or have permission to test)</span><input className="input" value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com"/></label>
        <div className="grid md:grid-cols-2 gap-3">
          <label className="block"><span className="label">Optional API Endpoint</span><input className="input" value={apiEndpoint} onChange={e=>setApiEndpoint(e.target.value)} placeholder="https://example.com/api/health"/></label>
          <label className="block"><span className="label">Mode</span><select className="input" value={mode} onChange={e=>setMode(e.target.value)}><option value="safe_external">Safe External Checks</option><option value="simulated">Simulated/Local Assessment</option></select></label>
        </div>
        <div className="flex gap-3 items-center"><button className="btn" onClick={run} disabled={loading}>{loading?"Running Resilience Test...":"Start Resilience Test"}</button><button className="btn-secondary" onClick={()=>onDiscover(url.trim())} disabled={loading||!url.trim()}>Discover Infrastructure</button><span className="text-xs text-slate-500">Timeout: {Math.round(API_TIMEOUT_MS/1000)}s</span></div>
        {err && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-3 rounded">{err}</div>}
      </div>
      <div className="bg-panel2 rounded-xl p-4 text-sm text-slate-300 border border-slate-800"><div className="font-medium text-white mb-2">Live workflow</div><ul className="list-disc ml-5 space-y-1 text-slate-400"><li>Validate URL</li><li>Run safe resilience checks</li><li>Auto-discover infrastructure</li><li>Update charts/graph</li><li>Feed remediation & simulation</li></ul></div>
    </div>

    {infra && <div className="card p-4"><div className="flex justify-between items-center mb-2"><div className="font-medium">Auto Infrastructure Graph</div><div className="text-xs text-slate-400">{discovery?.partial?"Partial discovery":"Discovery complete"} • {infra.nodes.length} nodes</div></div><InfraGraph infra={infra as any} onChange={()=>{}} editable={false} /></div>}
    {!infra && <div className="card p-6 text-slate-400">No infrastructure graph yet. Enter a URL and run test/discovery.</div>}

    {loading && <div className="card p-6 text-slate-300">Running real checks and updating visualizations...</div>}
    {res && <>
      <div className="grid lg:grid-cols-[260px_1fr_1fr] gap-4">
        <div className="card p-5 flex flex-col items-center justify-center"><ScoreRing score={res.overall_score}/><div className="mt-3 font-medium text-accent">{res.classification}</div><div className="text-xs text-slate-500 mt-1 text-center break-all">{res.url}</div></div>
        <div className="card p-4 h-72"><div className="font-medium mb-2">Factor Scores</div><ResponsiveContainer width="100%" height="90%"><BarChart data={factorData}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="factor" stroke="#94a3b8" tick={{fontSize:10}} interval={0} angle={-15} height={50}/><YAxis domain={[0,100]} stroke="#94a3b8"/><Tooltip/><Bar dataKey="score" fill="#5b8cff"/></BarChart></ResponsiveContainer></div>
        <div className="card p-4 h-72"><div className="font-medium mb-2">Pass/Fail Distribution</div><ResponsiveContainer width="100%" height="90%"><PieChart><Pie data={statusData} dataKey="value" nameKey="name" outerRadius={90} label>{statusData.map((_,i)=><Cell key={i} fill={COLORS[i%COLORS.length]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer></div>
      </div>
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card p-4 h-72"><div className="font-medium mb-2">Resilience Radar</div><ResponsiveContainer width="100%" height="90%"><RadarChart data={factorData}><PolarGrid stroke="#334155"/><PolarAngleAxis dataKey="factor" tick={{fill:"#94a3b8",fontSize:10}}/><Radar dataKey="score" stroke="#5b8cff" fill="#5b8cff" fillOpacity={0.35}/></RadarChart></ResponsiveContainer></div>
        <div className="card p-4 h-72"><div className="font-medium mb-2">Response/Probe Latency (ms)</div><ResponsiveContainer width="100%" height="90%"><BarChart data={latencyData}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="name" stroke="#94a3b8" tick={{fontSize:10}}/><YAxis stroke="#94a3b8"/><Tooltip/><Bar dataKey="ms" fill="#14b8a6"/></BarChart></ResponsiveContainer></div>
      </div>
      <div className="card p-4"><div className="font-medium mb-2">Detailed Test Results</div><div className="overflow-auto"><table className="w-full text-sm"><thead className="text-slate-400"><tr><th className="text-left p-2">Test</th><th>Category</th><th>Status</th><th className="text-left">Detail</th></tr></thead><tbody>{(res.tests||[]).map((t:any,i:number)=><tr key={i} className="border-t border-slate-800"><td className="p-2">{t.name}{t.simulated?<span className="ml-2 text-[10px] text-amber-300">simulated</span>:null}</td><td className="text-center">{t.category}</td><td className={`text-center ${t.passed?"text-green-400":"text-red-400"}`}>{t.passed?"PASS":"FAIL"}</td><td className="p-2 text-slate-400">{t.detail}{t.error?` | ${t.error}`:""}</td></tr>)}</tbody></table></div><div className="mt-3 text-xs text-slate-500">{res.safety_note}</div></div>
    </>}
  </div>;
}
