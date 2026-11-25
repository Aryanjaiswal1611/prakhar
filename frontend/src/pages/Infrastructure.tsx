import { useEffect, useState } from "react";
import InfraGraph from "../components/graph/InfraGraph";
import type { Infrastructure, SimulationResult, WebsiteTestResult } from "../types";

export default function InfrastructurePage({infra, sim, websiteTest, discovery, selectedUrl, onDiscover}:{infra:Infrastructure|null; setInfra:(i:Infrastructure)=>void; sim:SimulationResult|null; websiteTest:WebsiteTestResult|null; discovery:any; selectedUrl:string; onDiscover:(url:string)=>Promise<void>}) {
  const [url, setUrl] = useState(selectedUrl || websiteTest?.url || "https://example.com");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  useEffect(()=>{ if(selectedUrl) setUrl(selectedUrl); },[selectedUrl]);
  const dInfra = discovery?.nodes ? {id:0,name:`Discovered: ${discovery.url}`,description:discovery.summary||"",nodes:discovery.nodes,edges:discovery.edges} : null;
  const fallbackInfra = infra;
  const shown = dInfra || fallbackInfra;
  const run = async () => { if(!url.trim()) return; setLoading(true); setErr(""); try{ await onDiscover(url.trim()); } catch(e:any){ setErr(e?.response?.data?.detail||e?.message||"Discovery failed"); } finally{ setLoading(false); } };
  return <div className="space-y-4">
    <div className="flex justify-between items-center"><h1 className="text-2xl font-semibold">Infrastructure Graph</h1><div className="flex gap-2"><input className="input w-80" value={url} onChange={e=>setUrl(e.target.value)} placeholder="https://example.com"/><button className="btn" onClick={run} disabled={loading}>{loading?"Discovering...":"Discover / Refresh"}</button></div></div>
    {err && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-3 rounded">{err}</div>}
    <div className="grid lg:grid-cols-[1fr_320px] gap-4">
      <div>{shown ? <InfraGraph infra={shown as any} simulation={sim} onChange={()=>{}} editable={false}/> : <div className="card p-8 text-slate-400">Enter a website URL to generate an infrastructure graph.</div>}</div>
      <div className="card p-4 space-y-3 text-sm">
        <div className="font-medium">Discovery Details</div>
        <div className="text-slate-400">Selected URL: <span className="text-slate-200 break-all">{selectedUrl || "none"}</span></div>
        <div className="text-slate-400">Source: <span className="text-slate-200">{dInfra ? "Live discovery/test data" : "Local sample infrastructure"}</span></div>
        <div className="text-slate-400">Nodes: <span className="text-slate-200">{shown?.nodes.length ?? 0}</span></div>
        <div className="text-slate-400">Edges: <span className="text-slate-200">{shown?.edges.length ?? 0}</span></div>
        {discovery?.partial && <div className="text-amber-300">Partial discovery: some checks failed; showing verified/inferred components only.</div>}
        <div className="border-t border-slate-800 pt-2"><div className="label mb-1">Components</div><div className="max-h-72 overflow-auto space-y-2">{(shown?.nodes||[]).map((n:any)=><div key={n.node_key} className="bg-panel2 p-2 rounded border border-slate-800"><div className="font-medium">{n.name}</div><div className="text-xs text-slate-400">{n.type} • {n.status} • {n.metadata?.confidence||"unknown"}</div></div>)}{!shown && <div className="text-slate-500">No data.</div>}</div></div>
      </div>
    </div>
  </div>;
}
