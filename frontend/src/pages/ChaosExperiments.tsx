import { useEffect, useState } from "react";
import axios from "axios";
import { chaosApi } from "../api/actions";
import type { Infrastructure, SimulationResult, WebsiteTestResult } from "../types";
import InfraGraph from "../components/graph/InfraGraph";

function errMsg(e:unknown){ if(axios.isAxiosError(e)){ const d=e.response?.data?.detail; if(typeof d==="string") return d; if(d?.message) return `${d.message}${d.recovery?` Recovery: ${d.recovery}`:""}`; if(!e.response) return "Backend server unavailable."; return `Request failed (${e.response.status}).`; } return e instanceof Error?e.message:"Simulation failed."; }

export default function ChaosExperiments({infra, onSim, selectedUrl, websiteTest, discovery}:{infra:Infrastructure|null; onSim:(s:SimulationResult)=>void; selectedUrl:string; websiteTest:WebsiteTestResult|null; discovery:any}) {
  const [predefined,setPredefined]=useState<any[]>([]);
  const [custom,setCustom]=useState<any[]>([]);
  const [url,setUrl]=useState(selectedUrl || websiteTest?.url || "https://example.com");
  const [target,setTarget]=useState("website");
  const [type,setType]=useState("server_failure");
  const [severity,setSeverity]=useState(4);
  const [duration,setDuration]=useState(30);
  const [endpoint,setEndpoint]=useState("");
  const [name,setName]=useState("Custom simulation");
  const [desc,setDesc]=useState("");
  const [running,setRunning]=useState(false);
  const [result,setResult]=useState<SimulationResult|null>(null);
  const [err,setErr]=useState("");
  useEffect(()=>{ chaosApi.predefined().then(setPredefined).catch(()=>{}); chaosApi.custom().then(setCustom).catch(()=>{}); },[]);
  useEffect(()=>{ if(selectedUrl) setUrl(selectedUrl); },[selectedUrl]);
  const dInfra = discovery?.nodes ? {id:0,name:`Discovered: ${discovery.url}`,description:discovery.summary||"",nodes:discovery.nodes,edges:discovery.edges} : infra;
  useEffect(()=>{ if(dInfra?.nodes?.length){ const has= dInfra.nodes.some((n:any)=>n.node_key===target); if(!has) setTarget(dInfra.nodes[0].node_key); } },[discovery?.url, infra?.id]);
  const run = async () => { setRunning(true); setErr(""); try { const r=await chaosApi.simulate({url:url.trim()||undefined,infrastructure_id:dInfra?.id||undefined, experiment:{experiment_type:type,target_node_key:target,severity,params:{duration_sec:duration,target_endpoint:endpoint||undefined}}, name, description:desc}); setResult(r); onSim(r);} catch(e:any){ setErr(errMsg(e)); } finally { setRunning(false);} };
  const saveCustom = async ()=>{ try{ await chaosApi.createCustom({name,description:desc,url:url.trim()||undefined,experiment_type:type,target_node_key:target,severity,duration_sec:duration,target_endpoint:endpoint||undefined,params:{}}); setCustom(await chaosApi.custom()); } catch(e:any){ setErr(errMsg(e)); } };
  return <div className="space-y-4">
    <h1 className="text-2xl font-semibold">Chaos Simulator</h1>
    <div className="grid lg:grid-cols-[380px_1fr] gap-4">
      <div className="card p-4 space-y-3">
        <label className="block"><span className="label">Website URL</span><input className="input" value={url} onChange={e=>setUrl(e.target.value)} /></label>
        <label className="block"><span className="label">Simulation Name</span><input className="input" value={name} onChange={e=>setName(e.target.value)} /></label>
        <label className="block"><span className="label">Description</span><input className="input" value={desc} onChange={e=>setDesc(e.target.value)} /></label>
        <label className="block"><span className="label">Target Component</span><select className="input" value={target} onChange={e=>setTarget(e.target.value)}>{(dInfra?.nodes||[]).map((n:any)=><option key={n.node_key} value={n.node_key}>{n.name} ({n.type})</option>)}</select></label>
        <label className="block"><span className="label">Failure Type</span><select className="input" value={type} onChange={e=>setType(e.target.value)}>{["server_failure","database_failure","network_latency","packet_loss","cpu_overload","memory_exhaustion","api_timeout","service_dependency_failure","website_unavailable","http_error"].map(t=><option key={t} value={t}>{t}</option>)}</select></label>
        <div className="grid grid-cols-2 gap-2"><label className="block"><span className="label">Severity: {severity}</span><input type="range" min={1} max={5} value={severity} onChange={e=>setSeverity(Number(e.target.value))} className="w-full"/></label><label className="block"><span className="label">Duration (s)</span><input className="input" type="number" min={1} max={300} value={duration} onChange={e=>setDuration(Number(e.target.value))}/></label></div>
        <label className="block"><span className="label">Target Endpoint (optional)</span><input className="input" value={endpoint} onChange={e=>setEndpoint(e.target.value)} placeholder="/api/health"/></label>
        <div className="flex gap-2"><button className="btn flex-1" onClick={run} disabled={running}>{running?"Running Simulation...":"Run Simulation"}</button><button className="btn-secondary" onClick={saveCustom}>Save Custom</button></div>
        {err && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-3 rounded">{err}</div>}
        <div className="border-t border-slate-800 pt-3"><div className="label mb-2">Predefined</div><div className="space-y-2 max-h-40 overflow-auto">{predefined.map(p=><button key={p.id} className="w-full text-left bg-panel2 p-2 rounded hover:bg-slate-700" onClick={()=>{setType(p.failure_type); setSeverity(p.default_severity); setName(p.name); setDesc(p.description||"");}}><div className="text-sm font-medium">{p.name}</div><div className="text-xs text-slate-400">{p.description}</div></button>)}</div></div>
        <div className="border-t border-slate-800 pt-3"><div className="label mb-2">Saved Custom</div><div className="space-y-2 max-h-40 overflow-auto">{custom.map(c=><button key={c.id} className="w-full text-left bg-panel2 p-2 rounded hover:bg-slate-700" onClick={()=>{setName(c.name); setDesc(c.description||""); setUrl(c.url||url); setType(c.experiment_type); setTarget(c.target_node_key||"website"); setSeverity(c.severity||3); setDuration(c.duration_sec||30); setEndpoint(c.target_endpoint||"");}}><div className="text-sm font-medium">{c.name}</div><div className="text-xs text-slate-400">{c.experiment_type} • sev {c.severity}</div></button>)}{!custom.length && <div className="text-xs text-slate-500">No custom simulations saved.</div>}</div></div>
      </div>
      <div className="space-y-4">
        {dInfra ? <InfraGraph infra={dInfra as any} simulation={result} onChange={()=>{}} editable={false}/> : <div className="card p-6 text-slate-400">Select/discover a URL to visualize infrastructure.</div>}
        {result && <div className="card p-4 space-y-3"><div className="font-medium">Simulation Report</div>
          <div className="grid grid-cols-4 gap-3 text-sm"><div className="bg-panel2 p-2 rounded"><div className="text-slate-400">Status</div><div className="font-semibold">{result.status||"completed"}</div></div><div className="bg-panel2 p-2 rounded"><div className="text-slate-400">Availability</div><div className="font-semibold">{result.impact.availability_pct}%</div></div><div className="bg-panel2 p-2 rounded"><div className="text-slate-400">Affected</div><div className="font-semibold">{result.impact.affected_count}/{result.impact.total_nodes}</div></div><div className="bg-panel2 p-2 rounded"><div className="text-slate-400">Resilience</div><div className="font-semibold">{result.resilience.score}</div></div></div>
          {result.report && <div className="text-sm text-slate-300">{result.report.summary} Recovery: {result.report.recovered?"recovered/stable":"affected components remain"}.</div>}
          {result.error && <div className="text-red-300 text-sm">Error ({result.error_type||"error"}): {result.error}</div>}
          <div className="text-xs text-slate-500">Mode: controlled simulation on dependency graph; no destructive attacks on public websites.</div>
        </div>}
      </div>
    </div>
  </div>;
}
