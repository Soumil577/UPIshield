"""
Pydantic Schemas for SIH26184 Cybercrime Intelligence Backend.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class Complaint(BaseModel):
    id: str
    case_id: str
    victim_name: str
    victim_phone: str
    victim_upi: str
    victim_account: str
    victim_bank: str
    fraud_category: str
    reported_amount: float
    incident_time: str
    reported_time: str
    status: str
    city: str


class CaseDetail(BaseModel):
    id: str
    title: str
    description: str
    category: str
    total_amount_lost: float
    created_at: str
    status: str
    complaints: List[Complaint] = []
    primary_mule_account: Optional[str] = None
    primary_mule_upi: Optional[str] = None
    risk_evaluation: Optional[Dict[str, Any]] = None


class EntityNode(BaseModel):
    id: str
    label: str
    type: str  # victim, mule_l1, mule_l2, runner_token, device, atm_csp, phone
    details: Dict[str, Any] = {}


class EntityEdge(BaseModel):
    source: str
    target: str
    label: str
    amount: Optional[float] = None
    timestamp: Optional[str] = None
    edge_type: str  # fund_transfer, device_binding, sim_link, cashout_attempt


class EntityNetworkGraph(BaseModel):
    nodes: List[EntityNode]
    edges: List[EntityEdge]
    central_mule_node: Optional[str] = None
    total_layers: int = 4
    summary: str


class CashoutLocation(BaseModel):
    id: str
    name: str
    type: str  # ATM, CSP (Customer Service Point / Micro-ATM / BC Agent)
    bank: str
    address: str
    city: str
    latitude: float
    longitude: float
    cctv_available: bool
    historical_fraud_count: int


class CashoutPredictionItem(BaseModel):
    rank: int
    location_id: str
    name: str
    type: str
    bank: str
    latitude: float
    longitude: float
    probability_score: float
    risk_level: str  # CRITICAL, HIGH, MODERATE
    distance_km: float
    estimated_time_window: str
    reason_factors: List[str]


class CashoutPredictionResponse(BaseModel):
    case_id: str
    target_amount: float
    predicted_locations: List[CashoutPredictionItem]
    model_version: str = "SIH-ML-Cashout-GradientTree-v1.0"
    methodology_note: str
    recommended_actions: List[str]


class AlertCreateRequest(BaseModel):
    case_id: str
    location_ids: List[str]
    target_agencies: List[str] = ["LEA_POLICE_CYBERCELL", "BANK_FRAUD_NODAL", "I4C_REGISTRY"]
    priority: str = "CRITICAL"
    custom_notes: Optional[str] = "Immediate tactical interception & debit freeze requested."


class AlertResponse(BaseModel):
    id: str
    case_id: str
    case_title: str
    priority: str
    target_agencies: List[str]
    predicted_locations: List[Dict[str, Any]]
    dispatched_at: str
    status: str
    action_code: str
    summary: str


class DashboardStats(BaseModel):
    total_complaints: int
    total_cases: int
    amount_at_risk: float
    high_risk_cases_count: int
    active_hotspots_count: int
    recent_complaints: List[Complaint]
    recent_alerts: List[AlertResponse]
    hotspot_locations: List[CashoutLocation]

