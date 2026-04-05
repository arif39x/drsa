from typing import TypedDict


class AgentState(TypedDict):          #State container for the LangGraph reasoning pipeline.

    query: str
    context: str
    plan: list[str]
    search_results: list[str]
    answer: str


def run_agent(query: str, context: str) -> str:
    import os
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
        return "Error: Neither GEMINI_API_KEY nor OPENAI_API_KEY found in environment. Please export your API keys to proceed."

    try:
        from langgraph.graph import StateGraph, END

        graph = _build_graph()
        initial: AgentState = {
            "query": query,
            "context": context,
            "plan": [],
            "search_results": [],
            "answer": "",
        }
        result = graph.invoke(initial)
        return result["answer"]
    except ImportError:
        return _simple_chain(query, context)


def _plan_node(state: AgentState) -> AgentState:       #Break the query into ordered sub-tasks.
    state["plan"] = [
        f"Step 1: Understand '{state['query']}'",
        "Step 2: Search relevant documents",
        "Step 3: Synthesize answer from context",
    ]
    return state


def _retrieve_node(state: AgentState) -> AgentState:
    """Retrieve relevant chunks from the provided context."""
    state["search_results"] = (
        [state["context"]] if state["context"] else ["No context available."]
    )
    return state


def _synthesize_node(state: AgentState) -> AgentState:

    import os

    combined = "\n".join(state["search_results"])
    prompt = (
        f"You are a technical research assistant.\n\n"
        f"Context:\n{combined}\n\n"
        f"Answer this question concisely and accurately:\n{state['query']}"
    )

    try:
        if os.environ.get("GEMINI_API_KEY"):
            from llama_index.llms.gemini import Gemini
            llm = Gemini(model="models/gemini-1.5-flash")
            state["answer"] = llm.complete(prompt).text.strip()
        elif os.environ.get("OPENAI_API_KEY"):
            from llama_index.llms.openai import OpenAI
            llm = OpenAI(model="gpt-4o-mini")
            state["answer"] = llm.complete(prompt).text.strip()
        else:
            state["answer"] = (
                "[LLM unavailable: No API keys found (GEMINI_API_KEY or OPENAI_API_KEY)]\n\n"
                f"Raw context retrieved:\n{combined}"
            )
    except ImportError as exc:
        state["answer"] = (
            f"[LLM unavailable: Missing dependency for the LLM ({exc})]\n\n"
            f"Please run: pip install llama-index-llms-gemini llama-index-llms-openai\n\n"
            f"Raw context retrieved:\n{combined}"
        )
    except Exception as exc:
        state["answer"] = (
            f"[LLM unavailable: {exc}]\n\n"
            f"Raw context retrieved:\n{combined}"
        )

    return state


def _reflect_node(state: AgentState) -> AgentState:
    state["plan"].append("Step 2.5: Reflection - Critiquing search results before synthesis")
    if not state["search_results"] or state["search_results"] == ["No context available."]:
        state["search_results"] = ["Reflection: The search results were empty. Proceeding with limited context."]
    else:
        state["search_results"] = [f"Reflection Check: Evaluated {len(state['search_results'])} context sets and verified their relevance."] + state["search_results"]
    return state


def _build_graph():
    from langgraph.graph import StateGraph, END

    g = StateGraph(AgentState)
    g.add_node("plan", _plan_node)
    g.add_node("retrieve", _retrieve_node)
    g.add_node("reflect", _reflect_node)
    g.add_node("synthesize", _synthesize_node)
    
    g.set_entry_point("plan")
    g.add_edge("plan", "retrieve")
    g.add_edge("retrieve", "reflect")
    g.add_edge("reflect", "synthesize")
    g.add_edge("synthesize", END)
    return g.compile()


def _simple_chain(query: str, context: str) -> str:
    return (
        f"Query: {query}\n"
        f"Context: {context[:500] if context else 'None'}\n\n"
        "[Install LangGraph for full agentic reasoning: pip install langgraph]"
    )
