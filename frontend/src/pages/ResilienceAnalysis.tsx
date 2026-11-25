import type { SimulationResult, WebsiteTestResult } from "../types";

export default function ResilienceAnalysis({sim, websiteTest}:{sim:SimulationResult|null; websiteTest:WebsiteTestResult|null}) {
  const web = websiteTest;
  return <div className="space-y-6">
    <h1 className="text-3xl font-semibold">Resilience Analysis</h1>
    {web && <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between"><div><div className="text-sm text-slate-400">Latest Website Test</div><div className="text-xl font-semibold">{web.url}</div></div><div className="text-right"><div className="text-3xl font-bold">{web.overall_score}</div><div className="text-accent">{web.classification}</div></div></div>
      <div className="grid md:grid-cols-3 gap-3">{Object.entries(web.factors).map(([k,v]:any)=><div key={k} className="bg-panel2 p-3 rounded border border-slate-800"><div className="text-slate-400 text-xs capitalize">{k.replaceAll("_"," ")}</div><div className="text-xl font-semibold">{v.score}<span className="text-xs text-slate-500">/100</span></div><div className="text-xs text-slate-500">weight {Math.round(v.weight*100)}% · weighted {v.weighted_score}</div></div>)}</div>
      <div className="text-sm text-slate-300"><span className="text-slate-400">How calculated: </span>Overall = Server×0.20 + API×0.20 + Network×0.15 + Backend×0.20 + Performance×0.15 + Security×0.10. Each factor score is 0-100 from actual safe checks and clearly labeled simulated stress checks.</div>
      <div className="bg-[#0a1222] border border-slate-800 rounded p-3 text-sm"><div className="font-medium mb-2">Inferred Failure Propagation Graph (labeled)</div>
        <div className="flex flex-wrap gap-2">{web.graph.nodes.map((n:any)=><div key={n.node_key} className={`px-3 py-2 rounded border text-xs ${n.status==="healthy"?"border-green-500/50 text-green-300":n.status==="warning"?"border-amber-500/50 text-amber-300":"border-red-500/50 text-red-300"}`}>{n.name}: {n.status}</div>)}</div>
        <div className="text-xs text-slate-500 mt-2">{web.graph.label}. Edges: {web.graph.edges.map((e:any)=>`${e.source_key}→${e.target_key}`).join(", ")}</div>
      </div>
    </div>}
    {!sim && !web && <div className="card p-6 text-slate-400">Run a website resilience test or chaos simulation to see analysis.</div>}
    {sim && <div className="card p-5"><div className="font-medium mb-2">Latest Chaos Simulation Analysis</div><div className="grid grid-cols-4 gap-4 mb-4"><div className="bg-panel2 p-3 rounded"><div className="text-slate-400 text-sm">Score</div><div className="text-2xl font-bold">{sim.resilience.score}</div><div className="text-accent">{sim.resilience.classification}</div></div><div className="bg-panel2 p-3 rounded"><div className="text-slate-400 text-sm">Failed</div><div className="text-2xl font-bold text-red-400">{sim.impact.failed_count ?? 0}</div></div><div className="bg-panel2 p-3 rounded"><div className="text-slate-400 text-sm">Affected</div><div className="text-2xl font-bold">{sim.impact.affected_count}</div></div><div className="bg-panel2 p-3 rounded"><div className="text-slate-400 text-sm">Recovery</div><div className="text-2xl font-bold">{sim.impact.estimated_recovery_sec}s</div></div></div>
    <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1">{sim.resilience.recommendations.map((r:string,i:number)=><li key={i}>{r}</li>)}</ul></div>}
  </div>;
}
