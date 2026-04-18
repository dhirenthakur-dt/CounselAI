from typing import TypedDict, Optional, List

class CounselState(TypedDict):
    """
    This is the shared memory between all agents.
    Each agent reads from here and writes back to here.
    """
    # What student typed
    user_message: str

    # Agent 1 output — student profile
    percentile: Optional[float]
    category: Optional[str]
    district: Optional[str]
    branches: Optional[List[str]]
    budget: Optional[int]
    hostel_needed: Optional[bool]

    # Agent 2 + 3 output — ranked colleges
    eligible_colleges: Optional[List[dict]]
    ranked_colleges: Optional[List[dict]]

    # Agent 4 output — strategy advice
    strategy: Optional[str]

    # Agent 5 output — document checklist
    documents: Optional[dict]

    # Final response shown to student
    final_response: Optional[str]

    # Conversation history
    messages: Optional[List[dict]]

    # Any error
    error: Optional[str]