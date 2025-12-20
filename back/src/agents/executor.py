from dataclasses import dataclass
from typing import Dict, List, Any, Callable, Optional
from src.agents.agent import Agent, AgentResponse
from src.core.models import AgentData, AgentType, AgentsMetrics, Status
from src.core.task import Tasks, PlannedTask
from src.agents.memory import MemoryAgent
from src.agents.vision import VisionAgent
from src.tools import classification_tool
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
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize Vision Agent
vision_agent = VisionAgent()


# --- Mock Tools for Registry (since actual files are missing/not provided) ---
def vision_tool(
    image_path: str, instruction: str, metrics: Optional[AgentsMetrics] = None
):
    if not metrics:
        return "[Error] Metrics needed for vision agent"

    full_response = ""
    try:
        for response in vision_agent.analyze(instruction, image_path, metrics):
            full_response += response.chunk
        return full_response
    except Exception as e:
        return f"Error executing vision agent: {e}"


def duckdb_tool(sql_query: str):
    return f"[MOCK] Résultat SQL pour '{sql_query}': 42 cases found."


def rag_tool(search_query: str):
    return f"[MOCK] Guidelines trouvées pour '{search_query}': Protocole standard appliqué."


# --- Tool Registry ---
TOOL_REGISTRY: Dict[str, Callable] = {
    "vision_tool": vision_tool,
    "duckdb_tool": duckdb_tool,
    "rag_tool": rag_tool,
    "classification_tool": classification_tool,
}


@dataclass
class ToolExecutor:
    function_name: str
    args: List[Any]


class ExecutorAgent(Agent):
    def __init__(self, agent_data: Optional[PlannedTask | AgentData] = None):
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
2. Sélectionne l'OUTIL le plus approprié UNIQUEMENT si cela est nécessaire.
3. Si l'instruction mentionne une variable (ex: '$step_1'), utilise-la TELLE QUELLE dans les arguments.
4. RENVOIE UNIQUEMENT L'APPEL DE L'OUTIL au format JSON.

Voici les tools mis a ta disposition:

---
    OUTIL 1: "vision_tool"
    DESCRIPTION: Analyse une image médicale.
    PARAMÈTRES: [image_path, instruction]
    OUTPUT: str (analyse textuelle)

    OUTIL 2: "classification_tool"
    DESCRIPTION: Classification d'image (Maligne/Bénigne).
    PARAMÈTRES: [image_path]
    OUTPUT: str (Diagnostic et confiance)

FORMAT JSON OBLIGATOIRE :
[
    {
        "function_name": "nom_de_l_outil",
        "args": ["arg1", "arg2"]
    }
]
"""
        super().__init__(
            system_prompt,
            AgentType.EXECUTOR,
            real_agent_data,
            model="google/gemma-3-27b-it:free",
        )

    def parse_tools(self, json_response: str) -> List[ToolExecutor]:
        try:
            cleaned_response = (
                json_response.replace("```json", "").replace("```", "").strip()
            )
            start = cleaned_response.find("[")
            end = cleaned_response.rfind("]")
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start : end + 1]

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

    def exec_tools(self, tool: ToolExecutor, metrics: AgentsMetrics) -> Any:
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
            clean_args = tool.args
            if tool.function_name == "vision_tool":
                result = tool_func(*clean_args, metrics=metrics)
            else:
                result = tool_func(*clean_args)

            logging.info(f"Tool '{tool.function_name}' executed. Result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error executing {tool.function_name}: {e}")
            return f"Error executing {tool.function_name}: {e}"

    def execute_task(
        self,
        task: PlannedTask,
        tasks: Tasks,
        metrics: AgentsMetrics,
        memory: MemoryAgent,
    ):
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
            yield AgentResponse(
                metrics=metrics,
                id=self.agent_data.id,
                chunk="\n\n**Erreur : Dépendances non satisfaites.**",
            )
            return

        tools_to_call = self.parse_tools(self.last_response)

        for tool in tools_to_call:
            try:
                original_args = tool.args
                tool.args = memory.resolve_args(tool.args)

                if tool.args != original_args:
                    yield AgentResponse(
                        metrics=metrics,
                        id=self.agent_data.id,
                        chunk=f"\n> *Mémoire : Résolution {original_args} -> {tool.args}*",
                    )
            except Exception as e:
                yield AgentResponse(
                    metrics=metrics,
                    id=self.agent_data.id,
                    chunk=f"\n**Erreur Mémoire : {e}**",
                )
                continue

            result = self.exec_tools(tool, metrics)
            memory.set(task.step_id, result)

            if result is not None:
                yield AgentResponse(
                    metrics=metrics,
                    id=self.agent_data.id,
                    chunk=f"\n\n**Résultat de l'outil '{tool.function_name}' :** {result}",
                )
