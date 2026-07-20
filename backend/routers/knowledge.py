from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from knowledge_graph.graph import knowledge_graph

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class PathRequest(BaseModel):
    source: str
    target: str


@router.get("/summary")
def graph_summary():
    return knowledge_graph.summary()


@router.get("/node-types")
def node_types():
    return knowledge_graph.node_types


@router.get("/edge-types")
def edge_types():
    return knowledge_graph.edge_types


@router.get("/nodes/{node_id}")
def get_node(node_id: str):
    if node_id not in knowledge_graph.graph:
        raise HTTPException(404, "Node not found")
    data = knowledge_graph.graph.nodes[node_id]
    edges = list(knowledge_graph.graph.edges(node_id, data=True))
    return {
        "id": node_id,
        "type": data.get("type"),
        "properties": dict(data),
        "outgoing_edges": [
            {"target": t, "relationship": d.get("type")} for _, t, d in edges
        ],
    }


@router.get("/neighbors/{node_id}")
def get_neighbors(node_id: str, depth: int = Query(1, ge=1, le=3)):
    if node_id not in knowledge_graph.graph:
        raise HTTPException(404, "Node not found")
    return {"node_id": node_id, "depth": depth, "neighbors": knowledge_graph.query_neighbors(node_id, depth)}


@router.post("/path")
def find_path(req: PathRequest):
    path = knowledge_graph.find_path(req.source, req.target)
    if not path:
        raise HTTPException(404, "No path found between specified nodes")
    return {"source": req.source, "target": req.target, "path": path}


@router.get("/nodes/type/{entity_type}")
def get_nodes_by_type(entity_type: str):
    subgraph = knowledge_graph.get_subgraph(entity_type)
    return subgraph
