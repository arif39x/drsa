"""
Layer 3: BRAIN – Agentic Reasoning
LangGraph state machine: plan → search → retrieve → synthesize → answer.
Called from Rust brain/agent_integration.rs via PyO3.
"""
from typing import TypedDict, Annotated
import operator


class AgentState(TypedDict):
    query: str
    context: str
    plan: list[str]
    search_results: list[str]
    answer: str


def run_agent(query: str, context: str) -> str:
    """
    Entry point called from Rust via PyO3.
    Runs a LangGraph agent that plans, searches, retrieves, and answers.
    """
    try:
        from langgraph.graph import StateGraph, END  # type: ignore
        graph = _build_graph()
        result = graph.invoke({"query": query, "context": context, "plan": [], "search_results": [], "answer": ""})
        return result["answer"]
    except ImportError:
        # If LangGraph not installed, use simple fallback
        return _simple_chain(query, context)


def _plan_node(state: AgentState) -> AgentState:
    """Break the query into sub-tasks."""
    state["plan"] = [f"Step 1: Understand '{state['query']}'", "Step 2: Search relevant documents", "Step 3: Synthesize answer"]
    return state


def _retrieve_node(state: AgentState) -> AgentState:
    """Retrieve relevant chunks from context."""
    state["search_results"] = [state["context"]] if state["context"] else ["No context available."]
    return state


def _synthesize_node(state: AgentState) -> AgentState:
    """Generate final answer from retrieved context."""
    # TODO: Replace with actual LLM call (local or cloud)
    combined = "\n".join(state["search_results"])
    state["answer"] = f"Based on the retrieved context:\n{combined}\n\nAnswer to '{state['query']}': (LLM synthesis pending)"
    return state


def _build_graph():
    """Build and compile the LangGraph state machine."""
    from langgraph.graph import StateGraph, END  # type: ignore
    g = StateGraph(AgentState)
    g.add_node("plan", _plan_node)
    g.add_node("retrieve", _retrieve_node)
    g.add_node("synthesize", _synthesize_node)
    g.set_entry_point("plan")
    g.add_edge("plan", "retrieve")
    g.add_edge("retrieve", "synthesize")
    g.add_edge("synthesize", END)
    return g.compile()


def _simple_chain(query: str, context: str) -> str:
    """Fallback when LangGraph is not installed."""
    return (
        f"Query: {query}\n"
        f"Context: {context[:500] if context else 'None'}\n"
        "(Install LangGraph for full agentic reasoning: pip install langgraph)"
    )
