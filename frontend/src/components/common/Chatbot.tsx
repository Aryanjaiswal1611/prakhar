import { useEffect, useState } from "react";
import { chatbotApi } from "../../api/actions";
import { MessageSquare, X, Send } from "lucide-react";
import type { ChatMessage, WebsiteTestResult } from "../../types";

export default function Chatbot({context}:{context:WebsiteTestResult|null}) {
  const [open,setOpen]=useState(false);
  const [input,setInput]=useState("");
  const [loading,setLoading]=useState(false);
  const [msgs,setMsgs]=useState<ChatMessage[]>([{role:"assistant",content:"Hi, I'm ChaosBrain AI Assistant. Ask me about the project, resilience scores, failures, or recommendations."}]);
  useEffect(()=>{ if(context) setMsgs(m=>[...m.slice(0,1), {role:"assistant",content:`I have context for ${context.url} (score ${context.overall_score}/100). Ask why it got this score or how to improve it.`}]); },[context?.id]);
  const send = async () => {
    const text=input.trim(); if(!text) return;
    setMsgs(m=>[...m,{role:"user",content:text}]); setInput(""); setLoading(true);
    try { const r=await chatbotApi.ask(text, context||undefined); setMsgs(m=>[...m,{role:"assistant",content:r.answer, source:r.source}]); }
    catch { setMsgs(m=>[...m,{role:"assistant",content:"Unable to reach chatbot API. Ensure backend is running."}]); }
    finally { setLoading(false); }
  };
  return <>
    <button onClick={()=>setOpen(!open)} className="fixed bottom-5 right-5 z-50 btn rounded-full shadow-lg flex items-center gap-2"><MessageSquare size={16}/>{open?"Close":"AI Assistant"}</button>
    {open && <div className="fixed bottom-20 right-5 z-50 w-[380px] max-w-[calc(100vw-2rem)] card shadow-2xl border-slate-700 overflow-hidden">
      <div className="p-3 border-b border-slate-800 flex justify-between items-center bg-panel2"><div><div className="font-medium">ChaosBrain AI Assistant</div><div className="text-[11px] text-slate-400">Rule-based fallback when AI key unavailable</div></div><button onClick={()=>setOpen(false)} className="text-slate-400 hover:text-white"><X size={16}/></button></div>
      <div className="h-80 overflow-auto p-3 space-y-2">
        {msgs.map((m,i)=><div key={i} className={`text-sm p-2 rounded-lg ${m.role==="user"?"bg-accent/20 ml-8":"bg-slate-800/80 mr-4"}`}><div>{m.content}</div>{m.source && <div className="text-[10px] text-slate-500 mt-1">{m.source}</div>}</div>)}
        {loading && <div className="text-sm text-slate-400">Thinking...</div>}
      </div>
      <div className="p-2 border-t border-slate-800 flex gap-2"><input className="input" value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()} placeholder="Ask about score, failures, project..."/><button className="btn" onClick={send}><Send size={14}/></button></div>
    </div>}
  </>;
}
