from asyncio import Task
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable
from src.agents.agent import Agent, AgentResponse
from src.core.models import AgentData, AgentType, AgentsMetrics, Status
from src.core.task import Tasks, PlannedTask
from src.agents.memory import MemoryAgent
from src.tools.test import add
import json
import logging
import os

# Configure logging
log_dir = os.path.join(os.getcwd(), "data", "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Mock Tools for Registry (since actual files are missing/not provided) ---
def vision_tool(image_path: str):
    return f"[MOCK] Analyse de l'image {image_path}: Masse suspecte détectée."

def duckdb_tool(sql_query: str):
    return f"[MOCK] Résultat SQL pour '{sql_query}': 42 cases found."

def rag_tool(search_query: str):
    return f"[MOCK] Guidelines trouvées pour '{search_query}': Protocole standard appliqué."

# --- Tool Registry ---
TOOL_REGISTRY: Dict[str, Callable] = {
    "add": add,
    "vision_tool": vision_tool,
    "duckdb_tool": duckdb_tool,
    "rag_tool": rag_tool
}

@dataclass
class ToolExecutor:
    function_name: str
    args: List[Any]


class ExecutorAgent(Agent):
    def __init__(self, agent_data: PlannedTask | AgentData = None):
        real_agent_data = None
        if isinstance(agent_data, PlannedTask):
            real_agent_data = AgentData(
                id=agent_data.step_id,
                type=AgentType.EXECUTOR,
                dependencies=agent_data.dependencies,
                status=agent_data.status,
            )
        else:
            real_agent_data = agent_data

        system_prompt = """

Role: System 
Tu es l'Exécuteur Clinique du système C.L.A.R.A.
Ton rôle est STRICTEMENT d'exécuter la tâche précise qui t'est donnée par le Planner.

INSTRUCTIONS:
1. Analyse la tâche reçue.
2. Sélectionne l'OUTIL le plus approprié.
3. Si l'instruction mentionne une variable (ex: '$step_1'), utilise-la TELLE QUELLE dans les arguments.
4. RENVOIE UNIQUEMENT L'APPEL DE L'OUTIL au format JSON.

Voici les tools mis a ta disposition:

---
    ---
    OUTIL 4 : "add"
    DESCRIPTION : Additionne deux nombres entiers.
    PARAMÈTRES : [a, b]
    OUTPUT: int
    ---

FORMAT JSON OBLIGATOIRE :
[
    {
        "function_name": "nom_de_l_outil",
        "args": ["arg1", "arg2"]
    }
]
"""
        super().__init__(system_prompt, AgentType.EXECUTOR,  real_agent_data, model="google/gemma-3-27b-it:free")

    def parse_tools(self, json_response: str) -> List[ToolExecutor]:
        try:
            cleaned_response = json_response.replace("```json", "").replace("```", "").strip()
            start = cleaned_response.find("[")
            end = cleaned_response.rfind("]")
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start:end+1]
                
            data = json.loads(cleaned_response)
            tasks = []
            for item in data:
                task = ToolExecutor(
                    function_name=item.get("function_name", ""),
                    args=item.get("args", []),
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            logging.error(f"Failed to parse json : {e}")
            return []

    def exec_tools(self, tool: ToolExecutor) -> Any:
        """
        Exécution générique via le TOOL_REGISTRY.
        Les arguments doivent DÉJÀ être résolus (pas de '$var').
        """
        tool_func = TOOL_REGISTRY.get(tool.function_name)
        
        if not tool_func:
            error_msg = f"Outil inconnu : {tool.function_name}"
            logging.error(error_msg)
            return f"Error: {error_msg}"

        try:
            # Conversion des arguments en types appropriés si nécessaire ?
            # Pour l'instant on passe les args tels quels.
            # add attend des int, vision attend str.
            # Si l'argument vient du JSON, c'est peut-être string "1".
            # Une conversion intelligente pourrait être ajoutée ici ou déléguée à l'outil.
            # Pour 'add', on caste en int si possible.
            
            clean_args = tool.args
            if tool.function_name == "add":
                 clean_args = [int(arg) for arg in tool.args]

            result = tool_func(*clean_args)
            logging.info(f"Tool '{tool.function_name}' executed. Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error executing {tool.function_name}: {e}")
            return f"Error executing {tool.function_name}: {e}"

    def execute_task(self, task: PlannedTask, tasks: Tasks, metrics: AgentsMetrics, memory: MemoryAgent):
        """
        Exécute la tâche en utilisant la mémoire partagée.
        """
        
        # 1. Validation Dépendances
        if tasks.dependencies_met(task):
            # Update status
            self.update_status(Status.PENDING, metrics, task)
            
            for response in self.ask(task.description, metrics):
                yield response

            self.update_status(Status.FINISHED, metrics, task)
        else:
            self.update_status(Status.BLOCKED, metrics, task)
            yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="\n\n**Erreur : Dépendances non satisfaites.**")
            return

        tools_to_call = self.parse_tools(self.last_response)
        
        for tool in tools_to_call:
            
            try:
                original_args = tool.args
                tool.args = memory.resolve_args(tool.args)
                
                if tool.args != original_args:
                    yield AgentResponse(metrics=metrics, id=self.agent_data.id, 
                                        chunk=f"\n> *Mémoire : Résolution {original_args} -> {tool.args}*")
            except Exception as e:
                yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk=f"\n**Erreur Mémoire : {e}**")
                continue

            result = self.exec_tools(tool)
            memory.set(task.step_id, result)
            
            if result is not None:
                yield AgentResponse(metrics=metrics, id=self.agent_data.id, 
                                    chunk=f"\n\n**Résultat de l'outil '{tool.function_name}' :** {result}")
