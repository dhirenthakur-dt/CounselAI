from typing import TypedDict, Optional, List

class CounselState(TypedDict):
    user_message: str
    percentile: Optional[float]
    category: Optional[str]
    district: Optional[str]
    branches: Optional[List[str]]
    budget: Optional[int]
    hostel_needed: Optional[bool]
    eligible_colleges: Optional[List[dict]]
    ranked_colleges: Optional[List[dict]]
    strategy: Optional[str]
    documents: Optional[dict]
    final_response: Optional[str]
    messages: Optional[List[dict]]
    error: Optional[str]