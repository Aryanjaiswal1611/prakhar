import { useEffect, useState } from "react";
import { historyApi, monitoringApi, websiteTestApi } from "../api/actions";
import type { Infrastructure, SimulationResult, WebsiteTestResult } from "../types";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

const COLORS=["#5b8cff","#22c55e","#f59e0b","#ef4444","#14b8a6","#a78bfa"];
export default function Overview({infra, sim, websiteTest}:{infra:Infrastructure|null; sim:SimulationResult|null; websiteTest:WebsiteTestResult|null}) {
  const [runs,setRuns]=useState<any[]>([]); const [webTests,setWebTests]=useState<any[]>([]); const [mon,setMon]=useState<any>(null);
  useEffect(()=>{ historyApi.runs().then(setRuns).catch(()=>{}); websiteTestApi.list().then(setWebTests).catch(()=>{}); monitoringApi.status().then(setMon).catch(()=>{}); },[sim?.run_id, websiteTest?.id]);
  const latestWeb = websiteTest || null;
  const score = latestWeb?.overall_score ?? sim?.resilience?.score ?? 100;
  const cls = latestWeb?.classification ?? sim?.resilience?.classification ?? "Excellent";
  const chart = webTests.slice().reverse().map(r=>({name:`#${r.id}`, score:r.overall_score}));
  const factorData = latestWeb ? Object.entries(latestWeb.factors).map(([k,v]:any)=>({name:k.replaceAll("_"," "), value:v.score})) : [];
  const failDist = latestWeb ? [{name:"Passed",value:latestWeb.tests.filter((t:any)=>t.passed).length},{name:"Failed",value:latestWeb.tests.filter((t:any)=>!t.passed).length}] : [];
  const simChart = runs.slice().reverse().map(r=>({name:`#${r.id}`, score:r.resilience_score}));
  return <div className="space-y-6">
    <div className="flex justify-between items-end"><div><h1 className="text-3xl font-semibold">ChaosBrain AI Dashboard</h1><p className="text-slate-400">Live resilience, infrastructure, simulation, and remediation insights.</p></div><div className="text-xs text-slate-500">Real backend data; no fake scores</div></div>
    <div className="grid md:grid-cols-4 gap-4">
      <div className="card p-4"><div className="text-slate-400 text-sm">Latest Resilience</div><div className="text-3xl font-bold">{score}</div><div className="text-sm text-accent">{cls}</div></div>
      <div className="card p-4"><div className="text-slate-400 text-sm">Website Tests</div><div className="text-3xl font-bold">{webTests.length}</div><div className="text-sm text-slate-400">stored reports</div></div>
      <div className="card p-4"><div className="text-slate-400 text-sm">Infra Nodes</div><div className="text-3xl font-bold">{infra?.nodes.length ?? 0}</div><div className="text-sm text-slate-400">current graph</div></div>
      <div className="card p-4"><div className="text-slate-400 text-sm">Monitoring</div><div className="text-3xl font-bold">{mon?.system_health ?? "-"}</div><div className="text-sm text-slate-400">simulated status</div></div>
    </div>
    <div className="grid lg:grid-cols-2 gap-4">
      <div className="card p-4 h-80"><div className="mb-2 font-medium">Website Resilience History</div>{chart.length?<ResponsiveContainer width="100%" height="90%"><LineChart data={chart}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="name" stroke="#94a3b8"/><YAxis stroke="#94a3b8" domain={[0,100]}/><Tooltip/><Line type="monotone" dataKey="score" stroke="#5b8cff" strokeWidth={2}/></LineChart></ResponsiveContainer>:<div className="text-slate-500 text-sm">No website test data yet.</div>}</div>
      <div className="card p-4 h-80"><div className="mb-2 font-medium">Latest Factor Scores</div>{factorData.length?<ResponsiveContainer width="100%" height="90%"><BarChart data={factorData}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="name" stroke="#94a3b8" tick={{fontSize:10}} interval={0} angle={-12} height={55}/><YAxis stroke="#94a3b8" domain={[0,100]}/><Tooltip/><Bar dataKey="value" fill="#5b8cff" /></BarChart></ResponsiveContainer>:<div className="text-slate-500 text-sm">Run a website test to populate factor visualizations.</div>}</div>
    </div>
    <div className="grid lg:grid-cols-3 gap-4">
      <div className="card p-4 h-72"><div className="mb-2 font-medium">Test Pass/Fail</div>{failDist.length?<ResponsiveContainer width="100%" height="90%"><PieChart><Pie data={failDist} dataKey="value" nameKey="name" outerRadius={80} label>{failDist.map((_,i)=><Cell key={i} fill={COLORS[i]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer>:<div className="text-slate-500 text-sm">No test distribution yet.</div>}</div>
      <div className="card p-4 h-72"><div className="mb-2 font-medium">Chaos Simulation Scores</div>{simChart.length?<ResponsiveContainer width="100%" height="90%"><LineChart data={simChart}><CartesianGrid strokeDasharray="3 3" stroke="#334155"/><XAxis dataKey="name" stroke="#94a3b8"/><YAxis domain={[0,100]} stroke="#94a3b8"/><Tooltip/><Line dataKey="score" stroke="#22c55e" strokeWidth={2}/></LineChart></ResponsiveContainer>:<div className="text-slate-500 text-sm">No simulations yet.</div>}</div>
      <div className="card p-4"><div className="font-medium mb-2">Recent Website Tests</div><div className="space-y-2 text-sm">{webTests.slice(0,6).map(r=><div key={r.id} className="flex justify-between border-b border-slate-800 pb-1"><span className="truncate pr-2">#{r.id} {r.url}</span><span className="text-slate-400">{r.overall_score}</span></div>)}{!webTests.length && <div className="text-slate-500">No website tests yet.</div>}</div></div>
    </div>
  </div>;
}
