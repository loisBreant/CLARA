from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from typing import List, Dict

class AgentType(Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    REACTIVE = "reactive"

class AgentData(BaseModel):
    id: UUID
    type: AgentType
    dependencies: List[UUID] = []
    
    input_token_count: float = 0.0
    output_token_count: float = 0.0
    time_taken: float = 0.0

class AgentsMetrics(BaseModel):
    agents: Dict[UUID, AgentData] = {}
    total_time: float = 0.0  # in seconds

class AgentResponse(BaseModel):
    metrics: AgentsMetrics
    id: UUID
    chunk: str