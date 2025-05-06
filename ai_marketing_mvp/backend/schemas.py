from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    ip: str

class ChatResponse(BaseModel):
    reply: str
