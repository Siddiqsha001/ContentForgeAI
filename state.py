from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkflowState:
    input: str
    step: int = 0
    outline: Optional[str] = None
    change_request: Optional[str] = None
    approved_outline: Optional[str] = None
    content: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[float] = None