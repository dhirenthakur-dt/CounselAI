from langgraph.graph import StateGraph, END
from agents.state import CounselState
from agents.profile_agent import profile_agent
from agents.eligibility_agent import eligibility_agent
from agents.strategy_agent import strategy_agent
from agents.document_agent import document_agent
from agents.response_agent import response_agent


def should_continue(state: dict) -> str:
    """Stop pipeline if any agent found an error."""
    if state.get("error"):
        return END
    return "continue"


def build_pipeline():
    """
    Build the LangGraph multi-agent pipeline.
    Agents run in sequence:
    Profile → Eligibility → Strategy → Document → Response
    """

    graph = StateGraph(CounselState)

    # Add all agents as nodes
    graph.add_node("profile_agent",     profile_agent)
    graph.add_node("eligibility_agent", eligibility_agent)
    graph.add_node("strategy_agent",    strategy_agent)
    graph.add_node("document_agent",    document_agent)
    graph.add_node("response_agent",    response_agent)

    # Set entry point
    graph.set_entry_point("profile_agent")

    # Connect agents in sequence
    graph.add_edge("profile_agent",     "eligibility_agent")
    graph.add_edge("eligibility_agent", "strategy_agent")
    graph.add_edge("strategy_agent",    "document_agent")
    graph.add_edge("document_agent",    "response_agent")
    graph.add_edge("response_agent",    END)

    return graph.compile()


# Create pipeline instance
pipeline = build_pipeline()
