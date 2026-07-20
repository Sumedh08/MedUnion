import networkx as nx
from typing import Optional, List, Any
from datetime import datetime
from core.logging import logger


class HealthcareKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_schema()

    def _build_schema(self):
        self.node_types = {
            "Hospital": {"color": "#3b82f6", "icon": "building"},
            "Patient": {"color": "#10b981", "icon": "user"},
            "District": {"color": "#f59e0b", "icon": "map"},
            "Disease": {"color": "#ef4444", "icon": "virus"},
            "Medicine": {"color": "#8b5cf6", "icon": "pill"},
            "Facility": {"color": "#06b6d4", "icon": "warehouse"},
            "Laboratory": {"color": "#ec4899", "icon": "flask"},
            "Staff": {"color": "#14b8a6", "icon": "stethoscope"},
            "Equipment": {"color": "#f97316", "icon": "tool"},
            "SupplyChain": {"color": "#6366f1", "icon": "truck"},
        }
        self.edge_types = {
            "located_in": {"color": "#6b7280"},
            "treated_at": {"color": "#3b82f6"},
            "diagnosed_with": {"color": "#ef4444"},
            "prescribed": {"color": "#8b5cf6"},
            "supplies": {"color": "#6366f1"},
            "reports_to": {"color": "#f59e0b"},
            "transfers_to": {"color": "#06b6d4"},
            "operates": {"color": "#f97316"},
        }

    def add_node(self, node_id: str, node_type: str, properties: Optional[dict] = None):
        if node_type not in self.node_types:
            logger.warning(f"Unknown node type: {node_type}")
        self.graph.add_node(node_id, type=node_type, **(properties or {}))

    def add_edge(self, source: str, target: str, edge_type: str, properties: Optional[dict] = None):
        if edge_type not in self.edge_types:
            logger.warning(f"Unknown edge type: {edge_type}")
        self.graph.add_edge(source, target, type=edge_type, **(properties or {}))

    def query_neighbors(self, node_id: str, depth: int = 1) -> list:
        if node_id not in self.graph:
            return []
        neighbors = list(nx.bfs_edges(self.graph, node_id, depth_limit=depth))
        result = []
        for source, target in neighbors:
            edge_data = self.graph.get_edge_data(source, target)
            result.append({
                "source": source,
                "source_type": self.graph.nodes[source].get("type"),
                "target": target,
                "target_type": self.graph.nodes[target].get("type"),
                "relationship": edge_data.get("type") if edge_data else None,
            })
        return result

    def find_path(self, source: str, target: str) -> list:
        try:
            path = nx.shortest_path(self.graph, source=source, target=target)
            return [{"node": n, "type": self.graph.nodes[n].get("type")} for n in path]
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def get_entity_type(self, node_id: str) -> Optional[str]:
        node = self.graph.nodes.get(node_id)
        return node.get("type") if node else None

    def get_subgraph(self, entity_type: str) -> dict:
        nodes = [(n, d) for n, d in self.graph.nodes(data=True) if d.get("type") == entity_type]
        return {"nodes": nodes, "count": len(nodes)}

    def summary(self) -> dict:
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "node_types": {t: self._count_type(t) for t in self.node_types},
            "edge_types": {t: self._count_edge_type(t) for t in self.edge_types},
        }

    def _count_type(self, node_type: str) -> int:
        return sum(1 for _, d in self.graph.nodes(data=True) if d.get("type") == node_type)

    def _count_edge_type(self, edge_type: str) -> int:
        return sum(1 for _, _, d in self.graph.edges(data=True) if d.get("type") == edge_type)

    def save_to_db(self, db):
        from sqlalchemy import text
        import json
        data = nx.node_link_data(self.graph)
        json_data = json.dumps(data)
        db.execute(text("CREATE TABLE IF NOT EXISTS system_state (key VARCHAR PRIMARY KEY, value JSONB)"))
        db.execute(text("INSERT INTO system_state (key, value) VALUES ('knowledge_graph', :val) ON CONFLICT (key) DO UPDATE SET value = :val"), {"val": json_data})
        db.commit()

    def load_from_db(self, db):
        from sqlalchemy import text
        from sqlalchemy.exc import ProgrammingError
        try:
            result = db.execute(text("SELECT value FROM system_state WHERE key = 'knowledge_graph'")).scalar()
            if result:
                import json
                data = json.loads(result) if isinstance(result, str) else result
                self.graph = nx.node_link_graph(data)
                return True
        except ProgrammingError:
            db.rollback()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to load knowledge graph from DB: {e}")
        return False


knowledge_graph = HealthcareKnowledgeGraph()


def init_knowledge_graph():
    from core.database import SessionLocal
    db = SessionLocal()
    try:
        if not knowledge_graph.load_from_db(db):
            rebuild_from_database(db)
    except Exception as e:
        logger.error(f"Failed to initialize knowledge graph from DB: {e}")
    finally:
        db.close()
    return knowledge_graph


def rebuild_from_database(db):
    from models.hospital.organization import Hospital
    from models.community.geography import District
    
    knowledge_graph.graph.clear()
    
    hospitals = db.query(Hospital).all()
    for h in hospitals:
        knowledge_graph.add_node(
            h.id,
            "Hospital",
            {"name": h.name, "district": "Unknown"}
        )
        knowledge_graph.add_node(
            "Unknown",
            "District",
            {"name": "Unknown"}
        )
        knowledge_graph.add_edge(h.id, "Unknown", "located_in")
        
    districts = db.query(District).all()
    for d in districts:
        knowledge_graph.add_node(
            d.id,
            "District",
            {"name": d.name}
        )
        
    logger.info(f"Knowledge graph rebuilt from database: {knowledge_graph.graph.number_of_nodes()} nodes")
    knowledge_graph.save_to_db(db)
    return knowledge_graph
