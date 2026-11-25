import { useEffect, useState } from "react";
import { remediationApi } from "../api/actions";
import type { SimulationResult, Remediation, WebsiteTestResult } from "../types";

export default function RemediationPage({sim, websiteTest, selectedUrl}:{sim:SimulationResult|null; websiteTest:WebsiteTestResult|null; selectedUrl:string}) {
  const [lang,setLang]=useState("python");
  const [items,setItems]=useState<Remediation[]>([]);
  const [loading,setLoading]=useState(false);
  const [err,setErr]=useState("");
  const targetType = websiteTest ? "website" : sim ? "simulation" : "none";
  const load = async ()=>{ try{ if(websiteTest) setItems(await remediationApi.byWebsiteTest(websiteTest.id)); else if(sim) setItems(await remediationApi.byRun(sim.run_id)); else setItems([]);}catch(e:any){ setErr(e?.response?.data?.detail||e?.message||"Failed to load remediations"); } };
  useEffect(()=>{ load(); },[sim?.run_id, websiteTest?.id]);
  const generate = async ()=>{ setLoading(true); setErr(""); try{
    if(websiteTest) await remediationApi.generate({website_test_id: websiteTest.id, language: lang, url: websiteTest.url});
    else if(sim) await remediationApi.generate({run_id: sim.run_id, language: lang, url: selectedUrl});
    else { setErr("Run a website test or simulation first."); return; }
    await load();
  }catch(e:any){ setErr(e?.response?.data?.detail||e?.message||"Generation failed"); } finally{setLoading(false);} };
  const validate = async (id:number)=>{ await remediationApi.validate(id); await load(); };
  const approve = async (id:number)=>{ await remediationApi.approve(id); await load(); };

  return <div className="space-y-4">
    <div className="flex items-center justify-between"><h1 className="text-2xl font-semibold">AI Remediation</h1>
      <div className="flex gap-2 items-center"><select className="input w-40" value={lang} onChange={e=>setLang(e.target.value)}><option value="python">Python</option><option value="javascript">JavaScript</option><option value="java">Java</option></select>
      <button className="btn" onClick={generate} disabled={loading}>{loading?"Generating...":"Generate Patch"}</button></div>
    </div>
    <div className="text-xs text-slate-300 bg-panel2 border border-slate-800 p-3 rounded">Source: {targetType==="website"?`Website test #${websiteTest?.id} (${websiteTest?.url})`:targetType==="simulation"?`Simulation #${sim?.run_id}`:"none"}. Patches are review-only; approval does not auto-apply to production.</div>
    <div className="text-xs text-amber-300 bg-amber-500/10 border border-amber-500/30 p-3 rounded">If LLM provider/API key is not configured, ChaosBrain uses rule-based remediation fallback. No silent failure.</div>
    {err && <div className="text-red-300 text-sm bg-red-500/10 border border-red-500/30 p-3 rounded">{err}</div>}
    <div className="space-y-4">{items.map(r=><div key={r.id} className="card p-4 space-y-3">
      <div className="flex justify-between"><div><div className="font-medium">Remediation #{r.id} <span className="text-xs text-slate-400">({r.source})</span></div><div className="text-sm text-slate-400">{r.failure_description}</div></div>
        <div className={`text-xs px-2 py-1 rounded h-fit ${r.validation.status==="passed"?"bg-green-500/20 text-green-300":r.validation.status==="failed"?"bg-red-500/20 text-red-300":"bg-slate-700 text-slate-300"}`}>{r.validation.status}</div></div>
      <div className="grid md:grid-cols-2 gap-3 text-sm"><div className="bg-panel2 p-3 rounded"><div className="label">Root Cause</div>{r.root_cause}</div><div className="bg-panel2 p-3 rounded"><div className="label">Recommendation</div>{r.recommendation}</div></div>
      <div className="bg-panel2 p-3 rounded text-sm"><div className="label">Affected Components</div>{r.affected_components.join(", ")||"None"}</div>
      <div><div className="label">Suggested Patch ({r.patch_language})</div><pre className="bg-[#0a1222] p-3 rounded overflow-auto text-xs border border-slate-800"><code>{r.patch_text}</code></pre></div>
      <div className="text-sm"><span className="text-slate-400">Expected improvement: </span>{r.expected_improvement}</div>
      <div className="text-xs text-slate-400">Validation checks: {r.validation.checks.map((c:any)=>`${c.name}:${c.ok?"ok":"fail"}`).join(" • ")}</div>
      <div className="flex gap-2"><button className="btn-secondary" onClick={()=>validate(r.id)}>Revalidate</button><button className="btn" onClick={()=>approve(r.id)} disabled={r.approved}>{r.approved?"Approved (reviewed)":"Approve for Review"}</button></div>
    </div>)}{items.length===0 && <div className="card p-6 text-slate-400">No remediations yet. Run a website test or simulation, then generate a patch.</div>}</div>
  </div>;
}
