from langgraph.graph import StateGraph, END
from agents.state import CounselState
from agents.profile_agent import profile_agent
from agents.eligibility_agent import eligibility_agent
from agents.strategy_agent import strategy_agent
from agents.document_agent import document_agent
from agents.response_agent import response_agent


def build_pipeline():
    graph = StateGraph(CounselState)

    graph.add_node("profile_agent",     profile_agent)
    graph.add_node("eligibility_agent", eligibility_agent)
    graph.add_node("strategy_agent",    strategy_agent)
    graph.add_node("document_agent",    document_agent)
    graph.add_node("response_agent",    response_agent)

    graph.set_entry_point("profile_agent")

    graph.add_edge("profile_agent",     "eligibility_agent")
    graph.add_edge("eligibility_agent", "strategy_agent")
    graph.add_edge("strategy_agent",    "document_agent")
    graph.add_edge("document_agent",    "response_agent")
    graph.add_edge("response_agent",    END)

    return graph.compile()


pipeline = build_pipeline()