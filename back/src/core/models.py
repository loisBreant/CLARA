from pydantic import BaseModel
from enum import Enum
from typing import List, Dict

class AgentType(Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    REACTIVE = "reactive"

class Status(Enum):
    QUEUED = "queued"
    PENDING = "pending"
    FINISHED = "finished"
    BLOCKED = "blocked"

class AgentData(BaseModel):
    id: str 
    type: AgentType
    dependencies: List[str] = []
    status: Status = Status.QUEUED
    
    input_token_count: float = 0.0
    output_token_count: float = 0.0
    time_taken: float = 0.0


class AgentsMetrics(BaseModel):
    agents: Dict[str, AgentData] = {}
    total_time: float = 0.0  # in seconds

class AgentResponse(BaseModel):
    metrics: AgentsMetrics
    id: str 
    chunk: str
