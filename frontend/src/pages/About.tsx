export default function About() {
  return <div className="space-y-6 max-w-6xl">
    <div className="card p-8 bg-gradient-to-br from-panel to-panel2 border-accent/20">
      <div className="text-sm text-accent font-medium mb-2">Project Overview</div>
      <h1 className="text-4xl font-bold mb-3">ChaosBrain AI</h1>
      <p className="text-slate-300 max-w-3xl">Graph-Driven Continuous Resilience Simulator and Auto-Remediation Patch Generator. A professional platform to test website reliability, simulate controlled failures, analyze failure propagation, calculate resilience scores, and suggest remediation.</p>
    </div>

    <div className="grid md:grid-cols-2 gap-4">
      <section className="card p-5"><h2 className="text-xl font-semibold mb-2">Project Introduction</h2><p className="text-slate-300 text-sm">ChaosBrain AI helps developers and mentors evaluate how websites and software systems behave under failures. It combines safe website checks, graph-based dependency modeling, chaos simulation, resilience scoring, and AI-assisted/rule-based remediation guidance.</p></section>
      <section className="card p-5"><h2 className="text-xl font-semibold mb-2">Problem Statement</h2><p className="text-slate-300 text-sm">Modern websites fail due to server outages, API errors, network latency, database faults, backend dependency failures, and misconfigurations. These failures often propagate across components, causing downtime. ChaosBrain AI makes these risks visible and measurable before real incidents occur.</p></section>
    </div>

    <section className="card p-5"><h2 className="text-xl font-semibold mb-3">Project Objectives</h2>
      <div className="grid md:grid-cols-5 gap-3 text-sm">{["Detect possible failure points","Simulate website/system failures","Analyze failure propagation","Calculate resilience score","Suggest improvements & remediation"].map((o,i)=><div key={i} className="bg-panel2 border border-slate-800 rounded-lg p-3"><div className="text-accent font-bold mb-1">0{i+1}</div>{o}</div>)}</div>
    </section>

    <section className="card p-5"><h2 className="text-xl font-semibold mb-3">System Architecture</h2>
      <div className="bg-[#0a1222] border border-slate-800 rounded-xl p-4 text-sm overflow-auto">
        <pre className="text-slate-300">{`User/Mentor
   │
   ▼
React + Vite Dashboard  ─── Chatbot UI ─── Reports/Charts
   │ REST API
   ▼
FastAPI Backend
   ├─ Website Resilience Testing Engine (safe HTTP/HTTPS checks)
   ├─ Graph Engine (NetworkX dependency model)
   ├─ Chaos Simulation Engine (controlled failure injection)
   ├─ Resilience Analyzer (weighted 0-100 scoring)
   ├─ AI/Rule-based Remediation Engine
   └─ SQLite History & Reports`}</pre>
      </div>
    </section>

    <section className="card p-5"><h2 className="text-xl font-semibold mb-3">Working Methodology</h2>
      <div className="grid md:grid-cols-4 gap-3 text-sm">{[
        ["1. Input","User enters URL or selects infrastructure graph."],
        ["2. Test/Simulate","Safe checks run on target; chaos failures injected in controlled model."],
        ["3. Analyze","Propagation, impact, factor scores, and weighted resilience score computed."],
        ["4. Report & Improve","Dashboard, report, chatbot explanation, and remediation suggestions generated."]
      ].map(([t,d])=><div key={t} className="bg-panel2 p-3 rounded border border-slate-800"><div className="font-medium text-accent">{t}</div><div className="text-slate-300 mt-1">{d}</div></div>)}</div>
    </section>

    <div className="grid md:grid-cols-2 gap-4">
      <section className="card p-5"><h2 className="text-xl font-semibold mb-3">Technologies Used</h2>
        <div className="space-y-2 text-sm">{[["React + Vite + TypeScript","Frontend SPA and interactive UI"],["Tailwind CSS","Modern responsive styling"],["React Flow","Graph visualization for infrastructure/failure propagation"],["Recharts","Dashboard charts and score visualizations"],["FastAPI + Pydantic","Backend REST APIs and validation"],["SQLAlchemy + SQLite","Persistence for test/simulation history"],["NetworkX","Graph modeling and dependency traversal"],["Pytest","Backend testing"]].map(([k,v])=><div key={k} className="flex justify-between border-b border-slate-800 py-1"><span className="text-slate-200">{k}</span><span className="text-slate-400">{v}</span></div>)}</div>
      </section>
      <section className="card p-5"><h2 className="text-xl font-semibold mb-3">Applications</h2>
        <ul className="list-disc ml-5 text-sm text-slate-300 space-y-1"><li><b>Web developers</b> - identify reliability bottlenecks before release.</li><li><b>Software testers</b> - run structured resilience/failure scenarios.</li><li><b>DevOps engineers</b> - evaluate dependency and recovery risks.</li><li><b>Students</b> - learn chaos engineering and resilience concepts.</li><li><b>System administrators</b> - monitor health and plan mitigation.</li></ul>
      </section>
    </div>

    <div className="grid md:grid-cols-2 gap-4">
      <section className="card p-5"><h2 className="text-xl font-semibold mb-2">Advantages</h2><ul className="list-disc ml-5 text-sm text-slate-300 space-y-1"><li>Visual graph-based failure propagation.</li><li>Clear weighted resilience score with explanation.</li><li>Safe external testing + controlled simulations.</li><li>Remediation suggestions and report history.</li><li>Mentor-friendly project explanation in-app.</li></ul></section>
      <section className="card p-5"><h2 className="text-xl font-semibold mb-2">Limitations</h2><ul className="list-disc ml-5 text-sm text-slate-300 space-y-1"><li>External website tests are non-invasive and limited; cannot perform destructive/DoS tests.</li><li>Internal infra for external sites is inferred/simulated unless known.</li><li>Patch validation is static/simulated, not full production CI/CD.</li><li>AI chatbot uses rule-based fallback when no LLM key is configured.</li></ul></section>
    </div>
  </div>;
}
