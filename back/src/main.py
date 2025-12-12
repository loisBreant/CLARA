import uvicorn
import os
import shutil
import json
import uuid
import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.agents.oncology_agent import OncologyAgentSystem
from src.core.llm_client import LLMClient
from src.tools.database_tool import DatabaseTool

app = FastAPI(
    title="Onco-Agent API",
    description="API REST Asynchrone pour le système multi-agents",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

base_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(base_dir, "../data/inputs")
log_file = os.path.join(base_dir, "../data/logs/costs.csv")

os.makedirs(input_dir, exist_ok=True)
taks_store: Dict[str, Dict[str, Any]] = {}

@app.get("/health")
def health_check():
    return {"status": "running", "mode": "async"}

@app.get("/metrics")
def get_metrics():
    if not os.path.exists(log_file):
        return {"total_cost_usd": 0.0, "total_tokens": 0, "logs": []}
    try:
        df = pd.read_csv(log_file)
        if df.empty: 
            return {"total_cost_usd": 0.0, "total_tokens": 0, "logs": []}
        
        total_cost = pd.to_numeric(df['estimated_cost_usd'], errors='coerce').sum()
        total_tokens = pd.to_numeric(df['total_tokens'], errors='coerce').sum()
        logs = df.tail(50).fillna("").to_dict(orient="records")
        
        return {"total_cost_usd": total_cost, "total_tokens": int(total_tokens), "logs": logs}
    except Exception as e:
        return {"error": str(e)}

def run_agent_background(task_id: str, file_path: str, patient_data: Dict[str, Any]):
    """Fonction exécutée en arrière-plan par FastAPI"""
    try:
        taks_store[task_id]["status"] = "processing"
        taks_store[task_id]["progress"] = "Initialisation des agents..."
        
        # Callback pour mettre à jour le statut en temps réel
        def update_progress(msg):
            taks_store[task_id]["progress"] = msg
        
        agent_system = OncologyAgentSystem(scenario_id=task_id) # On utilise task_id comme scenario_id pour simplicité
        
        # Exécution avec callback
        results = agent_system.run_pipeline(file_path, patient_data, status_callback=update_progress)
        
        results["scenario_id"] = task_id
        taks_store[task_id]["result"] = results
        taks_store[task_id]["status"] = "completed"
        taks_store[task_id]["progress"] = "Analyse terminée."
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        taks_store[task_id]["status"] = "error"
        taks_store[task_id]["error"] = str(e)

@app.post("/analyze_async")
async def analyze_case_async(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    patient_json: str = Form(...)
):
    """
    Lance l'analyse et retourne immédiatement un ID de tâche.
    """
    try:
        # 1. Parsing
        patient_data = json.loads(patient_json)
        
        # 2. Save File
        file_ext = file.filename.split(".")[-1]
        task_id = str(uuid.uuid4())[:8]
        unique_filename = f"{task_id}.{file_ext}"
        file_path = os.path.join(input_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. Init Task State
        taks_store[task_id] = {
            "status": "pending",
            "progress": "Mise en file d'attente...",
            "result": None
        }
        
        # 4. Schedule Background Task
        background_tasks.add_task(run_agent_background, task_id, file_path, patient_data)
        
        return {"task_id": task_id, "message": "Analyse démarrée en arrière-plan"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    """Permet au Frontend de poller l'état de l'avancement."""
    task = taks_store.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# --- CHAT DB (Reste synchrone car rapide) ---
class ChatRequest(BaseModel):
    question: str

@app.post("/chat-db")
async def chat_with_db(request: ChatRequest):
    try:
        scenario_id = str(uuid.uuid4())[:8]
        agent_system = OncologyAgentSystem(scenario_id=scenario_id)
        response = agent_system.run_chat_mode(request.question)
        response["scenario_id"] = scenario_id
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
