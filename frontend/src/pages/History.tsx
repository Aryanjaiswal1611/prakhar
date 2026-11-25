import { useEffect, useState } from "react";
import { historyApi, websiteTestApi } from "../api/actions";
import type { WebsiteTestResult } from "../types";

export default function HistoryPage({onSelectRun, onSelectWebsiteTest}:{onSelectRun:(id:number)=>void; onSelectWebsiteTest:(r:WebsiteTestResult)=>void}) {
  const [runs,setRuns]=useState<any[]>([]);
  const [web,setWeb]=useState<any[]>([]);
  useEffect(()=>{ historyApi.runs().then(setRuns).catch(()=>{}); websiteTestApi.list().then(setWeb).catch(()=>{}); },[]);
  const loadWeb = async (id:number)=>{ const r = await websiteTestApi.get(id); onSelectWebsiteTest(r); };
  const download = async (id:number)=>{ const r = await websiteTestApi.get(id); const blob=new Blob([JSON.stringify(r,null,2)],{type:"application/json"}); const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=`resilience-report-${id}.json`; a.click(); };
  return <div className="space-y-6">
    <h1 className="text-3xl font-semibold">Reports & History</h1>
    <div className="card p-4"><div className="font-medium mb-3">Website Resilience Reports</div>
      <div className="overflow-auto"><table className="w-full text-sm"><thead className="text-slate-400"><tr><th className="text-left py-2">ID</th><th className="text-left">URL</th><th>Score</th><th>Class</th><th>Mode</th><th>Date</th><th></th></tr></thead>
      <tbody>{web.map(r=><tr key={r.id} className="border-t border-slate-800"><td className="py-2">#{r.id}</td><td className="max-w-[280px] truncate">{r.url}</td><td className="text-center">{r.overall_score}</td><td className="text-center">{r.classification}</td><td className="text-center">{r.test_mode}</td><td className="text-center text-slate-400">{new Date(r.created_at).toLocaleString()}</td><td className="text-right space-x-2"><button className="btn-secondary" onClick={()=>loadWeb(r.id)}>View</button><button className="btn-secondary" onClick={()=>download(r.id)}>Download</button></td></tr>)}
      {web.length===0 && <tr><td colSpan={7} className="py-6 text-center text-slate-500">No website tests yet.</td></tr>}</tbody></table></div>
    </div>
    <div className="card p-4"><div className="font-medium mb-3">Chaos Simulation History</div>
      <table className="w-full text-sm"><thead className="text-slate-400"><tr><th className="text-left py-2">Run</th><th className="text-left">Experiment</th><th>Target</th><th>Score</th><th>Date</th><th></th></tr></thead>
      <tbody>{runs.map(r=><tr key={r.id} className="border-t border-slate-800"><td className="py-2">#{r.id}</td><td>{r.experiment_type}</td><td className="text-center">{r.target_node_key}</td><td className="text-center">{r.resilience_score}</td><td className="text-center text-slate-400">{new Date(r.created_at).toLocaleString()}</td><td className="text-right"><button className="btn-secondary" onClick={()=>onSelectRun(r.id)}>Load</button></td></tr>)}
      {runs.length===0 && <tr><td colSpan={6} className="py-6 text-center text-slate-500">No simulation history yet.</td></tr>}</tbody></table>
    </div>
  </div>;
}
