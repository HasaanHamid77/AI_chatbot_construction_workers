from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="user | assistant | system")
    content: str


class SourceRef(BaseModel):
    document: str
    section: Optional[str] = None
    page: Optional[int] = None


class ChatRequest(BaseModel):
    messages: List[Message]
    mode: str = Field(
        default="auto", description="auto | wellbeing | technical"
    )


class ChatResponse(BaseModel):
    reply: str
    citations: List[SourceRef] = Field(default_factory=list)
    safety_notes: Optional[str] = None

