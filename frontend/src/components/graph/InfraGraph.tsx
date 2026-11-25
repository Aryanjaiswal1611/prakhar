import { useCallback, useEffect, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MiniMap, addEdge, useNodesState, useEdgesState, MarkerType } from "@xyflow/react";
import type { Connection, Node, Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import StatusNode from "./StatusNode";
import type { Infrastructure, GraphNode, GraphEdge, SimulationResult } from "../../types";

const nodeTypes = {status: StatusNode};

function toFlow(infra: Infrastructure, sim?: SimulationResult|null): {nodes: Node[]; edges: Edge[]} {
  const statuses = sim?.node_statuses || {};
  return {
    nodes: infra.nodes.map(n => ({
      id: n.node_key, type:"status", position:{x:n.x,y:n.y},
      data:{label:n.name, status: statuses[n.node_key] || n.status, nodeType:n.type, raw:n}
    })),
    edges: infra.edges.map(e => ({ id:e.edge_key, source:e.source_key, target:e.target_key, markerEnd:{type:MarkerType.ArrowClosed}, animated: !!sim && (statuses[e.source_key]==="failed" || statuses[e.target_key]==="warning" || statuses[e.target_key]==="failed"), style:{stroke: e.critical?"#64748b":"#475569"} }))
  };
}

export default function InfraGraph({infra, simulation, onChange, editable=true}:{infra:Infrastructure; simulation?:SimulationResult|null; onChange:(n:GraphNode[],e:GraphEdge[])=>void; editable?:boolean}) {
  const init = useMemo(()=>toFlow(infra, simulation), [infra.id]); // eslint-disable-line
  const [nodes, setNodes, onNodesChange] = useNodesState(init.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(init.edges);
  const [selected, setSelected] = useState<string|null>(null);

  useEffect(()=>{ const f=toFlow(infra, simulation); setNodes(f.nodes); setEdges(f.edges); }, [infra, simulation, setNodes, setEdges]);

  const emit = useCallback((ns:Node[], es:Edge[]) => {
    const gn: GraphNode[] = ns.map(n=>{ const raw=(n.data as any).raw as GraphNode; return {...raw, x:n.position.x, y:n.position.y, name:(n.data as any).label, status:(n.data as any).status, type:(n.data as any).nodeType}; });
    const ge: GraphEdge[] = es.map(e=>({edge_key:e.id, source_key:e.source, target_key:e.target, dependency_type:"sync", critical:true}));
    onChange(gn, ge);
  }, [onChange]);

  const onConnect = useCallback((c:Connection)=>{ if(!editable) return; const es = addEdge({...c, id:`e${Date.now()}`, markerEnd:{type:MarkerType.ArrowClosed}}, edges); setEdges(es); emit(nodes, es); }, [edges, nodes, editable, setEdges, emit]);
  const onNodeDragStop = useCallback((_ :any, __:any, ns:Node[])=> emit(ns, edges), [edges, emit]);

  return <div className="h-[520px] card overflow-hidden">
    <ReactFlow nodes={nodes} edges={edges} onNodesChange={(chs)=>{onNodesChange(chs);}} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeDragStop={onNodeDragStop} nodeTypes={nodeTypes} onNodeClick={(_,n)=>setSelected(n.id)} fitView>
      <Background />
      <MiniMap />
      <Controls />
    </ReactFlow>
    {selected && <div className="px-3 py-2 text-xs text-slate-400 border-t border-slate-800">Selected: {selected}</div>}
  </div>;
}
