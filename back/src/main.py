import uvicorn
import os
import uuid
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Generator

from fastapi.responses import StreamingResponse

from src.agents.planner import PlannerAgent
from src.agents.executor import ExecutorAgent
from src.agents.agent import AgentResponse
from src.core.models import AgentsMetrics

app = FastAPI(
    title="Onco-Agent API",
    description="API REST Asynchrone pour le système multi-agents",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,  # type:ignore
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chats = {} # how stored chats

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "../data/inputs")

os.makedirs(input_dir, exist_ok=True)

@app.get("/health")
def health_check():
    return {"status": "running", "mode": "async"}


class ChatRequest(BaseModel):
    question: str
    session_id: uuid.UUID


class ChatSession(BaseModel):
    session_id: uuid.UUID


@app.post("/init-session")
async def init_session() -> ChatSession:
    session_id = uuid.uuid4()
    chats[session_id] = {
        "planner": PlannerAgent(),
        "metrics": AgentsMetrics(),
    }
    return ChatSession(session_id=session_id)

def chat_generator(session_id: uuid.UUID, question: str) -> Generator[str, None, None]:
    planner = chats[session_id]["planner"]
    metrics = chats[session_id]["metrics"] 
    start_time = time.time()
 
    try:
        for response in planner.plan(question, metrics):
            yield create_chunk(response)
    except Exception as e:
        yield create_chunk(AgentResponse(metrics=metrics, id=planner.agent_data.id, chunk=f"**Erreur :** {str(e)}"))
        raise e

    metrics.total_time = time.time() - start_time
    yield create_chunk(AgentResponse(metrics=metrics, id=planner.agent_data.id, chunk=""))

def create_chunk(agent_response: AgentResponse) -> str:
    return agent_response.model_dump_json() + "\n"

@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(chat_generator(request.session_id, request.question), media_type="application/x-ndjson")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
