import uvicorn
import os
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fastapi.responses import StreamingResponse

from src.agents.planner import PlannerAgent

app = FastAPI(
    title="Onco-Agent API",
    description="API REST Asynchrone pour le système multi-agents",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware, # type:ignore
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


# @app.get("/metrics")
# def get_metrics():
#     if not os.path.exists(log_file):
#         return {"total_cost_usd": 0.0, "total_tokens": 0, "logs": []}
#     try:
#         df = pd.read_csv(log_file)
#         if df.empty:
#             return {"total_cost_usd": 0.0, "total_tokens": 0, "logs": []}
#
#         total_cost = pd.to_numeric(df['estimated_cost_usd'], errors='coerce').sum()
#         total_tokens = pd.to_numeric(df['total_tokens'], errors='coerce').sum()
#         logs = df.tail(50).fillna("").to_dict(orient="records")
#
#         return {"total_cost_usd": total_cost, "total_tokens": int(total_tokens), "logs": logs}
#     except Exception as e:
#         return {"error": str(e)}


class ChatRequest(BaseModel):
    question: str
    session_id: str


class ChatSession(BaseModel):
    session_id: uuid.UUID


@app.post("/init-session")
async def init_session() -> ChatSession:
    id = uuid.uuid4()
    chats[id] = {"planner": PlannerAgent()}
    return ChatSession(session_id=id)


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    agent = PlannerAgent()
    return StreamingResponse(agent.ask(request.question))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
