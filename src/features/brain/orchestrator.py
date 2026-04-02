from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class ResearchState(TypedDict):
    query: str
    mode: str
    plan: List[str]
    context: str
    results: List[str]
    current_step: int

def plan_step(state: ResearchState):
    # Generate a research plan based on the mode
    state["plan"] = [f"Step 1: Analyze {state['query']} in {state['mode']} context", "Step 2: Retrieve hierarchical data", "Step 3: Synthesize report"]
    return state

def analysis_step(state: ResearchState):
    # Execute the current research step.
    state["context"] = f"Contextual data for {state['query']}..."
    return state

def build_orchestrator():
    # Build the LangGraph state machine.
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", plan_step)
    workflow.add_node("analyzer", analysis_step)

    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "analyzer")
    workflow.add_edge("analyzer", END)

    return workflow.compile()
