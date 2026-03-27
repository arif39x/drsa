"""
Layer 3: STUDIO – Knowledge Graph
GLiNER NER entity extraction → NetworkX graph → Kuzu DB persistence.
Provides node/edge data for the WebGL KnowledgeGraphView.
"""
from typing import TypedDict


class Node(TypedDict):
    id: str
    label: str
    group: str


class Edge(TypedDict):
    source: str
    target: str
    label: str


class KnowledgeGraph(TypedDict):
    nodes: list[Node]
    edges: list[Edge]


def build_graph(text: str) -> KnowledgeGraph:
    """
    Extract entities and relations from text using GLiNER,
    then construct and persist a NetworkX graph in Kuzu DB.
    """
    entities = _extract_entities(text)
    relations = _extract_relations(text, entities)

    nodes: list[Node] = [{"id": e["text"], "label": e["text"], "group": e["label"]} for e in entities]
    edges: list[Edge] = [{"source": r["head"], "target": r["tail"], "label": r["relation"]} for r in relations]

    _persist_to_kuzu(nodes, edges)
    return {"nodes": nodes, "edges": edges}


def get_graph() -> KnowledgeGraph:
    """Retrieve the persisted knowledge graph from Kuzu DB."""
    try:
        import kuzu  # type: ignore
        db = kuzu.Database("drsa_kg.db")
        conn = kuzu.Connection(db)
        nodes_result = conn.execute("MATCH (n:Entity) RETURN n.id, n.label, n.group")
        edges_result = conn.execute("MATCH (a:Entity)-[r:RELATION]->(b:Entity) RETURN a.id, b.id, r.label")
        nodes = [{"id": row[0], "label": row[1], "group": row[2]} for row in nodes_result.get_as_df().values]
        edges = [{"source": row[0], "target": row[1], "label": row[2]} for row in edges_result.get_as_df().values]
        return {"nodes": nodes, "edges": edges}
    except Exception:
        return {"nodes": [], "edges": []}


def _extract_entities(text: str) -> list[dict]:
    try:
        from gliner import GLiNER  # type: ignore
        model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        labels = ["person", "organization", "location", "concept", "technology"]
        return model.predict_entities(text, labels, threshold=0.5)
    except ImportError:
        return []


def _extract_relations(text: str, entities: list[dict]) -> list[dict]:
    # TODO: Use GLiNER relation model or an LLM prompt for relation extraction
    return []


def _persist_to_kuzu(nodes: list[Node], edges: list[Edge]) -> None:
    try:
        import kuzu  # type: ignore
        db = kuzu.Database("drsa_kg.db")
        conn = kuzu.Connection(db)
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Entity(id STRING, label STRING, group STRING, PRIMARY KEY(id))")
        conn.execute("CREATE REL TABLE IF NOT EXISTS RELATION(FROM Entity TO Entity, label STRING)")
        for n in nodes:
            conn.execute(f"MERGE (e:Entity {{id: '{n['id']}', label: '{n['label']}', group: '{n['group']}'}})")
        for e in edges:
            conn.execute(f"MATCH (a:Entity {{id: '{e['source']}'}}), (b:Entity {{id: '{e['target']}'}}) CREATE (a)-[:RELATION {{label: '{e['label']}'}}]->(b)")
    except Exception:
        pass
