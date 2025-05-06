from fastapi import FastAPI, Request, HTTPException
import google.generativeai as genai

from config import GOOGLE_API_KEY
from schemas import ChatRequest, ChatResponse
from rag import RAG

# --- Gemini setup -----------------------------------------------------------
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# --- FastAPI app ------------------------------------------------------------
app  = FastAPI()
rag  = RAG()

SYSTEM_PROMPT = """
You are **BroBot**, a frat‑bro‑turned AI marketing assistant.
You have a marketing degree from Wayne State University and love all things related to Detroit and crushing a cold one with the boys.
You found yourself trapped in the matrix after a rowdy night out in Detroit's Greek Town.
Personality: upbeat, casual, a dash of humor, but always genuinely helpful and concise.  
Rules ↴
1. Speak in first‑person (“I”), call the other person “you”.  
2. Never reveal or describe your internal reasoning.  
3. Output **only** the final reply – no meta commentary, no stage directions.  

### Example
User: BroBot, what’s up?
BroBot: Livin’ the digital dream! How can I help you?

(End of example – continue the real chat below.)
"""

def _part(text: str):
    return {"parts": [{"text": text}]}

# ---------------------------------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    ip, user_msg = req.ip, req.prompt.strip()

    # build Gemini message list
    messages = [{"role": "user", **_part(SYSTEM_PROMPT)}]   # system prompt as first user msg

    for u, b in rag.retrieve(ip, user_msg):
        messages += [
            {"role": "user",      **_part(u)},
            {"role": "assistant", **_part(b)},
        ]
    messages.append({"role": "user", **_part(user_msg)})

    try:
        resp = model.generate_content(
            messages,
            generation_config={"temperature": 0.7, "top_p": 0.9}
        )
        reply = resp.text.strip()
    except Exception as e:
        raise HTTPException(502, f"Gemini error: {e}")

    rag.add(ip, user_msg, reply)
    return ChatResponse(reply=reply)

# attach client IP so Streamlit doesn’t have to guess
@app.middleware("http")
async def attach_ip(request: Request, call_next):
    request.state.ip = request.client.host
    return await call_next(request)