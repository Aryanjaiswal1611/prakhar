export type NodeStatus = "healthy" | "warning" | "failed" | "recovering" | "unknown";
export interface GraphNode { node_key: string; name: string; type: string; status: NodeStatus; criticality: number; x: number; y: number; metadata: Record<string, any>; }
export interface GraphEdge { edge_key: string; source_key: string; target_key: string; dependency_type: string; critical: boolean; }
export interface Infrastructure { id: number; name: string; description: string; nodes: GraphNode[]; edges: GraphEdge[]; }
export interface ChaosExperiment { experiment_type: string; target_node_key: string; severity: number; params?: Record<string, any>; }
export interface SimulationResult {
  run_id: number; infrastructure_id: number; experiment: ChaosExperiment; initial_failure: string;
  node_statuses: Record<string, NodeStatus>; affected_nodes: string[];
  propagation_path: {order:number; from_node:string; to_node:string; reason:string; resulting_status:string}[];
  impact: {availability_pct:number; affected_count:number; estimated_recovery_sec:number; total_nodes:number; failed_count?:number; warning_count?:number; healthy_count?:number};
  resilience: {score:number; classification:string; factors:any; single_points_of_failure:any[]; recommendations:string[]};
  recommendations: string[]; events: any[];
  status?: string; error?: string|null; error_type?: string|null; url?: string|null;
  baseline?: any; verification?: any; comparison?: any; report?: any;
}
export interface Remediation {
  id:number; run_id?:number|null; website_test_id?:number|null; url?:string|null; source:string; failure_description:string; root_cause:string; affected_components:string[];
  recommendation:string; patch_language:string; patch_text:string; expected_improvement:string;
  validation:{status:string; checks:any[]; logs:string[]}; approved:boolean;
}
export interface FactorScore { score:number; weight:number; weighted_score:number; passed:number; failed:number; details:any[]; summary:string; }
export interface WebsiteTestResult {
  id:number; url:string; test_mode:string; created_at:string; overall_score:number; classification:string;
  factors: Record<string, FactorScore>; tests:any[]; critical_issues:string[]; warnings:string[]; recommendations:string[];
  graph:{label:string; url:string; nodes:any[]; edges:any[]}; report_summary:string; safety_note:string;
  discovered_infrastructure?: any; timed_out?: boolean; duration_ms?: number;
}
export interface ChatMessage { role:"user"|"assistant"; content:string; source?:string; }
