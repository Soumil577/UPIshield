import {
  DashboardStats,
  Complaint,
  CaseDetail,
  EntityNetworkGraph,
  CashoutPredictionResponse,
  CashoutLocation,
  AlertResponse,
  AlertCreateRequest
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch dashboard stats: ${res.statusText}`);
  return res.json();
}

export async function fetchComplaints(caseId?: string): Promise<Complaint[]> {
  const url = caseId ? `${API_BASE}/complaints?case_id=${encodeURIComponent(caseId)}` : `${API_BASE}/complaints`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch complaints: ${res.statusText}`);
  return res.json();
}

export async function fetchComplaintById(id: string): Promise<Complaint> {
  const res = await fetch(`${API_BASE}/complaints/${encodeURIComponent(id)}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch complaint ${id}: ${res.statusText}`);
  return res.json();
}

export async function fetchCases(): Promise<CaseDetail[]> {
  const res = await fetch(`${API_BASE}/cases`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch cases: ${res.statusText}`);
  return res.json();
}

export async function fetchCaseById(id: string): Promise<CaseDetail> {
  const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(id)}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch case ${id}: ${res.statusText}`);
  return res.json();
}

export async function fetchCaseNetwork(caseId: string): Promise<EntityNetworkGraph> {
  const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/network`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch network graph for ${caseId}: ${res.statusText}`);
  return res.json();
}

export async function predictCashout(caseId: string): Promise<CashoutPredictionResponse> {
  const res = await fetch(`${API_BASE}/cases/${encodeURIComponent(caseId)}/predict-cashout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store"
  });
  if (!res.ok) throw new Error(`Failed to predict cashout for ${caseId}: ${res.statusText}`);
  return res.json();
}

export async function fetchLocations(city?: string): Promise<CashoutLocation[]> {
  const url = city ? `${API_BASE}/locations?city=${encodeURIComponent(city)}` : `${API_BASE}/locations`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch locations: ${res.statusText}`);
  return res.json();
}

export async function fetchAlerts(): Promise<AlertResponse[]> {
  const res = await fetch(`${API_BASE}/alerts`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch alerts: ${res.statusText}`);
  return res.json();
}

export async function createAlert(req: AlertCreateRequest): Promise<AlertResponse> {
  const res = await fetch(`${API_BASE}/alerts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!res.ok) throw new Error(`Failed to dispatch alert: ${res.statusText}`);
  return res.json();
}

