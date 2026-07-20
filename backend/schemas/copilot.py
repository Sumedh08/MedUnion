from pydantic import BaseModel
from typing import Optional, List


class CopilotQuery(BaseModel):
    message: str
    context: Optional[dict] = None
    conversation_id: Optional[str] = None


class CopilotResponse(BaseModel):
    answer: str
    data_sources: List[str]
    confidence: float
    follow_up_questions: List[str]
    visualizations: Optional[List[dict]] = None


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[dict]
    context: Optional[dict] = None
