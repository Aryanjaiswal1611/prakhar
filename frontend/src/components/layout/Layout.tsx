import { NavLink } from "react-router-dom";
import { Activity, Network, Flame, Shield, Wrench, History, Settings, Globe, BookOpen } from "lucide-react";

const items = [
  {to:"/", label:"Dashboard", icon:Activity},
  {to:"/testing-lab", label:"Testing Lab", icon:Globe},
  {to:"/infrastructure", label:"Infrastructure", icon:Network},
  {to:"/chaos", label:"Chaos Sim", icon:Flame},
  {to:"/resilience", label:"Resilience", icon:Shield},
  {to:"/remediation", label:"AI Remediation", icon:Wrench},
  {to:"/history", label:"Reports & History", icon:History},
  {to:"/about", label:"About Project", icon:BookOpen},
  {to:"/settings", label:"Settings", icon:Settings},
];

export default function Layout({children}:{children:React.ReactNode}) {
  return <div className="min-h-screen grid grid-cols-[250px_1fr] bg-bg">
    <aside className="bg-[#090f1c]/95 border-r border-slate-800 p-4 sticky top-0 h-screen">
      <div className="mb-8 px-2">
        <div className="text-xl font-bold text-white tracking-tight">ChaosBrain <span className="text-accent">AI</span></div>
        <div className="text-xs text-slate-400">Resilience & Reliability Platform</div>
      </div>
      <nav className="space-y-1">
        {items.map(i=>{const Icon=i.icon; return <NavLink key={i.to} to={i.to} end={i.to==="/"} className={({isActive})=>`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition ${isActive?"bg-accent/15 text-accent border border-accent/20":"text-slate-300 hover:bg-slate-800/70"}`}><Icon size={16}/>{i.label}</NavLink>})}
      </nav>
      <div className="absolute bottom-4 left-4 right-4 text-[11px] text-slate-500 border-t border-slate-800 pt-3">
        Safe testing only. External checks are low-volume; destructive failure injection is simulated.
      </div>
    </aside>
    <main className="p-6 overflow-auto min-w-0">{children}</main>
  </div>;
}
