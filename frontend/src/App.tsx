import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Overview from "./pages/Overview";
import InfrastructurePage from "./pages/Infrastructure";
import ChaosExperiments from "./pages/ChaosExperiments";
import ResilienceAnalysis from "./pages/ResilienceAnalysis";
import RemediationPage from "./pages/Remediation";
import HistoryPage from "./pages/History";
import SettingsPage from "./pages/Settings";
import TestingLab from "./pages/TestingLab";
import About from "./pages/About";
import Chatbot from "./components/common/Chatbot";
import { graphApi } from "./api/graph";
import { discoveryApi, historyApi } from "./api/actions";
import type { Infrastructure, SimulationResult, WebsiteTestResult } from "./types";

export default function App() {
  const [infra, setInfra] = useState<Infrastructure|null>(null);
  const [sim, setSim] = useState<SimulationResult|null>(null);
  const [websiteTest, setWebsiteTest] = useState<WebsiteTestResult|null>(null);
  const [selectedUrl, setSelectedUrl] = useState("");
  const [discovery, setDiscovery] = useState<any|null>(null);
  const [err, setErr] = useState("");

  useEffect(()=>{ (async()=>{
    try {
      const list = await graphApi.list();
      if (list.length) setInfra(list[0]);
      else { const created = await graphApi.create({name:"Default",description:"",nodes:[],edges:[]}); setInfra(created); }
    } catch(e:any){ setErr(e?.message||"Failed to load backend. Ensure backend is running on :8000."); }
  })(); },[]);

  const loadRun = async (id:number) => {
    const r = await historyApi.run(id);
    setSim({run_id:r.id, infrastructure_id:r.infrastructure_id, experiment:{experiment_type:r.experiment_type,target_node_key:r.target_node_key,severity:r.severity}, ...r.result});
    if (r.result?.url) setSelectedUrl(r.result.url);
  };

  const onWebsiteResult = async (r:WebsiteTestResult) => {
    setWebsiteTest(r);
    setSelectedUrl(r.url);
    if (r.discovered_infrastructure) setDiscovery(r.discovered_infrastructure);
    else {
      try { setDiscovery(await discoveryApi.infrastructure(r.url)); } catch {}
    }
  };

  const refreshDiscovery = async (url:string) => {
    setSelectedUrl(url);
    try { setDiscovery(await discoveryApi.infrastructure(url)); } catch (e:any) { setErr(e?.response?.data?.detail || e?.message || "Discovery failed"); }
  };

  return <BrowserRouter>
    <Layout>
      {err && <div className="mb-4 bg-red-500/10 border border-red-500/30 text-red-300 p-3 rounded">{err}</div>}
      <Routes>
        <Route path="/" element={<Overview infra={infra} sim={sim} websiteTest={websiteTest} />} />
        <Route path="/testing-lab" element={<TestingLab onResult={onWebsiteResult} latest={websiteTest} discovery={discovery} onDiscover={refreshDiscovery} selectedUrl={selectedUrl} />} />
        <Route path="/infrastructure" element={<InfrastructurePage infra={infra} setInfra={setInfra} sim={sim} websiteTest={websiteTest} discovery={discovery} selectedUrl={selectedUrl} onDiscover={refreshDiscovery} />} />
        <Route path="/chaos" element={<ChaosExperiments infra={infra} onSim={setSim} selectedUrl={selectedUrl} websiteTest={websiteTest} discovery={discovery} />} />
        <Route path="/resilience" element={<ResilienceAnalysis sim={sim} websiteTest={websiteTest} />} />
        <Route path="/remediation" element={<RemediationPage sim={sim} websiteTest={websiteTest} selectedUrl={selectedUrl} />} />
        <Route path="/history" element={<HistoryPage onSelectRun={loadRun} onSelectWebsiteTest={onWebsiteResult} />} />
        <Route path="/about" element={<About />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
      <Chatbot context={websiteTest} />
    </Layout>
  </BrowserRouter>;
}
