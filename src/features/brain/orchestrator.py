from typing import TypedDict, List

from src.features.brain.agentic_reasoning import run_agent


class ResearchState(TypedDict):

    query: str
    mode: str
    plan: List[str]
    context: str
    results: List[str]
    current_step: int


def plan_step(state: ResearchState) -> ResearchState:
    """Generate a research plan based on the active mode."""
    state["plan"] = [
        f"Step 1: Analyse '{state['query']}' in {state['mode']} context",
        "Step 2: Retrieve hierarchical data",
        "Step 3: Synthesise expert report",
    ]
    return state


def analysis_step(state: ResearchState) -> ResearchState:
    context = state.get("context", "")
    synthesised = run_agent(state["query"], context)
    state["context"] = synthesised
    state["results"] = [synthesised]
    return state


def build_orchestrator():
    try:
        from langgraph.graph import StateGraph, END

        workflow = StateGraph(ResearchState)
        workflow.add_node("planner", plan_step)
        workflow.add_node("analyzer", analysis_step)
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "analyzer")
        workflow.add_edge("analyzer", END)
        return workflow.compile()
    except ImportError:
        # Return a minimal stub so the TUI can still instantiate
        class _StubOrchestrator:
            def invoke(self, state: dict) -> dict:
                state["results"] = [
                    "[LangGraph not installed. Run: pip install langgraph]"
                ]
                return state

        return _StubOrchestrator()
