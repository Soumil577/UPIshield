export interface Complaint {
  id: string;
  case_id: string;
  victim_name: string;
  victim_phone: string;
  victim_upi: string;
  victim_account: string;
  victim_bank: string;
  fraud_category: string;
  reported_amount: number;
  incident_time: string;
  reported_time: string;
  status: string;
  city: string;
}

export interface RiskEvaluation {
  transaction_id?: string;
  user_id?: string;
  amount?: number;
  final_score: number;
  decision: "ALLOW" | "VERIFY" | "BLOCK";
  history_status: "NO_HISTORY" | "LIMITED_HISTORY" | "SUFFICIENT_HISTORY";
  general_score: number;
  general_reasons: string[];
  behavior_score: number;
  behavior_reasons: string[];
  human_readable_summary: string;
  evaluated_transactions_count?: number;
}

export interface CaseDetail {
  id: string;
  title: string;
  description: string;
  category: string;
  total_amount_lost: number;
  created_at: string;
  status: string;
  complaints: Complaint[];
  primary_mule_account?: string;
  primary_mule_upi?: string;
  risk_evaluation?: RiskEvaluation;
}

export interface EntityNode {
  id: string;
  label: string;
  type: "victim" | "mule_l1" | "mule_l2" | "runner_token" | "device" | "atm_csp" | "phone" | string;
  details?: Record<string, any>;
}

export interface EntityEdge {
  source: string;
  target: string;
  label: string;
  amount?: number;
  timestamp?: string;
  edge_type: string;
}

export interface EntityNetworkGraph {
  nodes: EntityNode[];
  edges: EntityEdge[];
  central_mule_node?: string;
  total_layers: number;
  summary: string;
}

export interface CashoutLocation {
  id: string;
  name: string;
  type: string; // ATM, CSP
  bank: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  cctv_available: boolean;
  historical_fraud_count: number;
}

export interface CashoutPredictionItem {
  rank: number;
  location_id: string;
  name: string;
  type: string;
  bank: string;
  latitude: number;
  longitude: number;
  probability_score: number;
  risk_level: "CRITICAL" | "HIGH" | "MODERATE";
  distance_km: number;
  estimated_time_window: string;
  reason_factors: string[];
}

export interface CashoutPredictionResponse {
  case_id: string;
  target_amount: number;
  predicted_locations: CashoutPredictionItem[];
  model_version: string;
  methodology_note: string;
  recommended_actions: string[];
}

export interface AlertCreateRequest {
  case_id: string;
  location_ids: string[];
  target_agencies?: string[];
  priority?: string;
  custom_notes?: string;
}

export interface AlertResponse {
  id: string;
  case_id: string;
  case_title: string;
  priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;
  target_agencies: string[];
  predicted_locations: Record<string, any>[];
  dispatched_at: string;
  status: "GENERATED" | "DISPATCHED" | "ACKNOWLEDGED" | "RESOLVED" | string;
  action_code: string;
  summary: string;
}

export interface DashboardStats {
  total_complaints: number;
  total_cases: number;
  amount_at_risk: number;
  high_risk_cases_count: number;
  active_hotspots_count: number;
  recent_complaints: Complaint[];
  recent_alerts: AlertResponse[];
  hotspot_locations: CashoutLocation[];
}

