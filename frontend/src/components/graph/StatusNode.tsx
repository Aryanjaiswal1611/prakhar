import { Handle, Position } from "@xyflow/react";
import type { NodeProps } from "@xyflow/react";

const colors: Record<string,string> = {healthy:"border-green-500", warning:"border-amber-500", failed:"border-red-500", recovering:"border-sky-500"};
const dot: Record<string,string> = {healthy:"bg-green-500", warning:"bg-amber-500", failed:"bg-red-500", recovering:"bg-sky-500"};

export default function StatusNode({data, selected}: NodeProps) {
  const status = (data.status || "healthy") as string;
  return <div className={`px-3 py-2 rounded-lg bg-panel2 border-2 ${colors[status]||"border-slate-600"} min-w-[150px] ${selected?"ring-2 ring-accent":""}`}>
    <Handle type="target" position={Position.Left} />
    <div className="flex items-center justify-between gap-2">
      <div className="font-medium text-sm">{data.label as string}</div>
      <span className={`w-2.5 h-2.5 rounded-full ${dot[status]||"bg-slate-500"}`}></span>
    </div>
    <div className="text-[11px] text-slate-400">{data.nodeType as string} · {status}</div>
    <Handle type="source" position={Position.Right} />
  </div>;
}
