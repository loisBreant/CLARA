import uvicorn
import os
import uuid
import time
from uuid import UUID

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

chats = {}

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "../data/inputs")
log_file = os.path.join(base_dir, "../data/logs/costs.csv")

os.makedirs(input_dir, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "running", "mode": "async"}


class ChatRequest(BaseModel):
    question: str
    session_id: str


class ChatSession(BaseModel):
    session_id: uuid.UUID


@app.post("/init-session")
async def init_session() -> ChatSession:
    id = uuid.uuid4()
    # On instancie les deux agents nécessaires pour la session
    chats[id] = {
        "planner": PlannerAgent(),
        "executor": ExecutorAgent()
    }
    return ChatSession(session_id=id)

def chat_generator(question: str) -> Generator[str, None, None]:
    """
    Générateur qui orchestre Planner + Executor et stream les résultats
    au format attendu par le frontend (AgentResponse JSONs).
    """
    planner = PlannerAgent()
    executor = ExecutorAgent()
    metrics = AgentsMetrics()
    start_time = time.time()
 
    try:
        for response in planner.plan(question, metrics):
            yield create_chunk(response)
    except Exception as e:
        yield create_chunk(AgentResponse(metrics=metrics, id=planner.data.id, chunk=f"**Erreur :** {str(e)}"))

    metrics.total_time = time.time() - start_time
    yield AgentResponse(metrics=metrics, id=executor.data.id, chunk="").model_dump_json() + "\n"

def create_chunk(agent_response: AgentResponse) -> str:
    return agent_response.model_dump_json() + "\n"

@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(chat_generator(request.question), media_type="application/x-ndjson")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
