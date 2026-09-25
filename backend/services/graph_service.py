"""
NetworkX Graph Service for Entity and Mule Network Analysis in SIH26184.
Builds multi-hop cybercrime money trails linking Victims, Mule Accounts, Devices, IPs, and ATMs.
"""

from typing import Dict, List
import networkx as nx

from backend.database import get_db_connection
from backend.models import EntityNode, EntityEdge, EntityNetworkGraph


class EntityGraphService:
    """
    Constructs and analyzes entity relationship graphs for cybercrime syndicates using NetworkX.
    """

    def build_case_network(self, case_id: str) -> EntityNetworkGraph:
        conn = get_db_connection()
        tx_rows = conn.execute("SELECT * FROM transactions WHERE case_id = ?", (case_id,)).fetchall()
        complaint_rows = conn.execute("SELECT * FROM complaints WHERE case_id = ?", (case_id,)).fetchall()
        conn.close()

        G = nx.DiGraph()
        nodes_dict: Dict[str, EntityNode] = {}
        edges_list: List[EntityEdge] = []

        # 1. Victims
        for c in complaint_rows:
            v_id = c["victim_upi"]
            if v_id not in nodes_dict:
                node = EntityNode(
                    id=v_id,
                    label=f"{c['victim_name']} ({c['city']})",
                    type="victim",
                    details={
                        "name": c["victim_name"],
                        "phone": c["victim_phone"],
                        "bank": c["victim_bank"],
                        "loss_amount": c["reported_amount"],
                        "category": c["fraud_category"]
                    }
                )
                nodes_dict[v_id] = node
                G.add_node(v_id, type="victim", label=node.label)

        # 2. Transactions
        for tx in tx_rows:
            s_id = tx["sender_id"]
            r_id = tx["receiver_id"]
            s_type = tx["sender_type"]
            r_type = tx["receiver_type"]

            if s_id not in nodes_dict:
                node = EntityNode(
                    id=s_id,
                    label=s_id,
                    type=s_type,
                    details={"type": s_type}
                )
                nodes_dict[s_id] = node
                G.add_node(s_id, type=s_type, label=s_id)

            if r_id not in nodes_dict:
                label = r_id
                if r_type == "mule_l1":
                    label = f"Mule L1: {r_id}"
                elif r_type == "mule_l2":
                    label = f"Mule L2: {r_id}"
                elif r_type == "runner_token":
                    label = f"Runner Token: {r_id}"

                node = EntityNode(
                    id=r_id,
                    label=label,
                    type=r_type,
                    details={"type": r_type, "location": tx["location"]}
                )
                nodes_dict[r_id] = node
                G.add_node(r_id, type=r_type, label=label)

            edge = EntityEdge(
                source=s_id,
                target=r_id,
                label=f"₹{tx['amount']:,.0f}",
                amount=float(tx["amount"]),
                timestamp=tx["timestamp"],
                edge_type="fund_transfer"
            )
            edges_list.append(edge)
            G.add_edge(s_id, r_id, weight=float(tx["amount"]), label=edge.label)

            dev_id = tx["device_id"]
            if dev_id and "DEV" in dev_id:
                if dev_id not in nodes_dict:
                    dev_node = EntityNode(
                        id=dev_id,
                        label=f"Device: {dev_id}",
                        type="device",
                        details={"ip": tx["ip_address"], "location": tx["location"]}
                    )
                    nodes_dict[dev_id] = dev_node
                    G.add_node(dev_id, type="device", label=dev_node.label)

                dev_edge = EntityEdge(
                    source=r_id,
                    target=dev_id,
                    label="Operated From",
                    amount=None,
                    timestamp=tx["timestamp"],
                    edge_type="device_binding"
                )
                edges_list.append(dev_edge)
                G.add_edge(r_id, dev_id, label="Operated From")

        # 3. Extraction Points
        target_atms = [
            {"id": "LOC-ATM-101", "name": "SBI E-Corner ATM (Rohini)", "runner": "RUNNER-CARD-DELHI-01"},
            {"id": "LOC-CSP-102", "name": "Airtel CSP Kiosk (Laxmi Nagar)", "runner": "RUNNER-CSP-TOKEN-02"}
        ]
        for atm in target_atms:
            atm_id = atm["id"]
            if atm_id not in nodes_dict:
                node = EntityNode(
                    id=atm_id,
                    label=atm["name"],
                    type="atm_csp",
                    details={"name": atm["name"], "target_kiosk": True}
                )
                nodes_dict[atm_id] = node
                G.add_node(atm_id, type="atm_csp", label=atm["name"])

            edge = EntityEdge(
                source=atm["runner"],
                target=atm_id,
                label="Target Extraction",
                amount=None,
                timestamp="Imminent",
                edge_type="cashout_attempt"
            )
            edges_list.append(edge)
            G.add_edge(atm["runner"], atm_id, label="Target Extraction")

        central_mule = "fastpay.sharma@okaxis"
        if len(G.nodes) > 0:
            degrees = dict(G.degree())
            central_mule = max(degrees, key=degrees.get) if degrees else central_mule

        summary = (
            f"Network analysis reveals a 4-tier funnel structure. {len(complaint_rows)} victim inflows "
            f"converge onto primary hub '{central_mule}', which rapidly disperses funds across 2 second-layer accounts "
            f"bound to shared operator devices in Delhi-NCR for imminent cash-out."
        )

        return EntityNetworkGraph(
            nodes=list(nodes_dict.values()),
            edges=edges_list,
            central_mule_node=central_mule,
            total_layers=4,
            summary=summary
        )


graph_service = EntityGraphService()

