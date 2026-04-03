import re
from typing import TypedDict


class Node(TypedDict): #A single entity node in the knowledge graph.

    id: str
    label: str
    group: str


class Edge(TypedDict): #A directed relation edge between two entity nodes.

    source: str
    target: str
    label: str


class KnowledgeGraph(TypedDict): #A complete knowledge graph with nodes, edges, and a Mermaid diagram.

    nodes: list[Node]
    edges: list[Edge]
    mermaid: str


def build_graph(text: str) -> KnowledgeGraph:

    entities = _extract_entities(text)
    relations = _extract_relations(text, entities)

    nodes: list[Node] = [
        {"id": e["text"], "label": e["text"], "group": e["label"]}
        for e in entities
    ]
    edges: list[Edge] = [
        {"source": r["head"], "target": r["tail"], "label": r["relation"]}
        for r in relations
    ]

    _persist_to_kuzu(nodes, edges)
    mermaid_str = build_mermaid({"nodes": nodes, "edges": edges, "mermaid": ""})

    return {"nodes": nodes, "edges": edges, "mermaid": mermaid_str}


def build_mermaid(graph: "KnowledgeGraph") -> str:

    lines = ["graph LR"]
    for node in graph["nodes"]:
        safe_id = _safe_id(node["id"])
        lines.append(f'    {safe_id}["{node["label"]} ({node["group"]})"]')
    for edge in graph["edges"]:
        src = _safe_id(edge["source"])
        tgt = _safe_id(edge["target"])
        lines.append(f'    {src} -->|"{edge["label"]}"| {tgt}')
    return "\n".join(lines)


def get_graph() -> KnowledgeGraph:

    try:
        import kuzu

        db = kuzu.Database("drsa_kg.db")
        conn = kuzu.Connection(db)
        nodes_result = conn.execute(
            "MATCH (n:Entity) RETURN n.id, n.label, n.group"
        )
        edges_result = conn.execute(
            "MATCH (a:Entity)-[r:RELATION]->(b:Entity) RETURN a.id, b.id, r.label"
        )
        nodes = [
            {"id": row[0], "label": row[1], "group": row[2]}
            for row in nodes_result.get_as_df().values
        ]
        edges = [
            {"source": row[0], "target": row[1], "label": row[2]}
            for row in edges_result.get_as_df().values
        ]
        mermaid_str = build_mermaid(
            {"nodes": nodes, "edges": edges, "mermaid": ""}
        )
        return {"nodes": nodes, "edges": edges, "mermaid": mermaid_str}
    except Exception:
        return {"nodes": [], "edges": [], "mermaid": "graph LR\n    _empty[No data]"}


def _extract_entities(text: str) -> list[dict]:

    try:
        from gliner import GLiNER

        model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
        labels = ["person", "organization", "location", "concept", "technology"]
        return model.predict_entities(text, labels, threshold=0.5)
    except ImportError:
        return []


def _extract_relations(text: str, entities: list[dict]) -> list[dict]:

    if not entities:
        return []

    entity_texts = [e["text"] for e in entities]
    sentences = re.split(r"[.!?]", text)
    relations: list[dict] = []

    for sentence in sentences:
        sentence_lower = sentence.lower()
        present = [e for e in entity_texts if e.lower() in sentence_lower]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                relations.append(
                    {
                        "head": present[i],
                        "tail": present[j],
                        "relation": "co-occurs-with",
                    }
                )

    return relations


def _persist_to_kuzu(nodes: list[Node], edges: list[Edge]) -> None:

    try:
        import kuzu

        db = kuzu.Database("drsa_kg.db")
        conn = kuzu.Connection(db)
        conn.execute(
            "CREATE NODE TABLE IF NOT EXISTS Entity("
            "id STRING, label STRING, group STRING, PRIMARY KEY(id))"
        )
        conn.execute(
            "CREATE REL TABLE IF NOT EXISTS RELATION("
            "FROM Entity TO Entity, label STRING)"
        )
        for n in nodes:
            safe_id = n["id"].replace("'", "''")
            safe_label = n["label"].replace("'", "''")
            safe_group = n["group"].replace("'", "''")
            conn.execute(
                f"MERGE (e:Entity {{id: '{safe_id}', "
                f"label: '{safe_label}', group: '{safe_group}'}})"
            )
        for e in edges:
            src = e["source"].replace("'", "''")
            tgt = e["target"].replace("'", "''")
            rel = e["label"].replace("'", "''")
            conn.execute(
                f"MATCH (a:Entity {{id: '{src}'}}), (b:Entity {{id: '{tgt}'}})"
                f" CREATE (a)-[:RELATION {{label: '{rel}'}}]->(b)"
            )
    except Exception:
        pass


def _safe_id(text: str) -> str:
    return re.sub(r"\W+", "_", text).strip("_") or "node"
