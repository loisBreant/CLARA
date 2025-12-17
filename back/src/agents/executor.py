from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from src.agents.agent import Agent, AgentResponse
from src.core.models import AgentType, AgentsMetrics, Status
from src.core.task import Tasks, PlannedTask
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

@dataclass
class ToolExecutor:
    function_name: str
    args: Any


class ExecutorAgent(Agent):
    def __init__(self):
        system_prompt = """

Role: System 
Tu es l'Exécuteur Clinique du système C.L.A.R.A.
Ton rôle est STRICTEMENT d'exécuter la tâche précise qui t'est donnée par le Planner.

INSTRUCTIONS:
1. Analyse la tâche reçue.
2. Sélectionne l'OUTIL le plus approprié parmi ceux disponibles.
3. Si la tâche nécessite un outil, RENVOIE UNIQUEMENT L'APPEL DE L'OUTIL au format JSON.
   - Si l'instruction mentionne une variable comme "$step_1", utilise-la telle quelle dans les arguments.
4. Si la tâche est une analyse textuelle ou une conclusion intermédiaire, réponds textuellement de manière concise.

Voici les tools mis a ta disposition:

---
    ---
    OUTIL 1 : "add"
    DESCRIPTION : Additionne deux nombres entiers.
    QUAND L'UTILISER : Pour effectuer des calculs simples d'addition.
    PARAMÈTRES : [a, b]
    OUTPUT: int
    ---

FORMAT JSON OBLIGATOIRE POUR LES OUTILS :
[
    {
        "function_name": "nom_de_l_outil",
        "args": ["arg1", "arg2"]
    }
]

"""
        super().__init__(system_prompt, AgentType.EXECUTOR, model="google/gemma-3-27b-it:free")
        self.last_tool_result = None

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

    def resolve_arguments(self, args: List[Any], context_results: Dict[str, Any]) -> List[Any]:
        """
        Remplace les arguments de type string commençant par '$' par leur valeur dans context_results.
        Ex: "$step_1" -> 3
        """
        resolved_args = []
        for arg in args:
            if isinstance(arg, str) and arg.startswith("$"):
                key = arg[1:] # remove '$'
                if key in context_results:
                    resolved_args.append(context_results[key])
                else:
                    # Fallback: keep as is if not found (maybe it's not a ref)
                    resolved_args.append(arg)
            else:
                resolved_args.append(arg)
        return resolved_args

    def exec_tools(self, tool: ToolExecutor, context_results: Dict[str, Any] = None) :
        if context_results:
            tool.args = self.resolve_arguments(tool.args, context_results)

        if tool.function_name == "add":
            try:
                # Ensure args are ints
                a = int(tool.args[0])
                b = int(tool.args[1])
                result = add(a, b)
                logging.info(f"Tool 'add' called with args: {tool.args}. Result: {result}")
                return result
            except Exception as e:
                logging.error(f"Error executing add: {e}")
                return f"Error: {e}"
        return None

    def execute_task(self, task: PlannedTask, tasks: Tasks, metrics: AgentsMetrics, context_results: Dict[str, Any]):
        """
        Exec a task
        """

        if tasks.dependencies_met(task):
            metrics.agents[self.agent_data.id].status = Status.PENDING
            task.status = Status.PENDING
            
            # On ajoute le contexte des résultats précédents à la description pour que l'agent comprenne
            # (optionnel, mais aide si l'agent doit faire du texte)
            # context_str = "\n".join([f"{k}: {v}" for k, v in context_results.items()])
            prompt = f"Voici la description de ta tache : \n{task.description}\n\nCONTEXTE VARIABLES:\n{context_results}"
            
            for response in self.ask(prompt, metrics):
                yield response

            metrics.agents[self.agent_data.id].status = Status.FINISHED
            task.status = Status.FINISHED
        else:
            task.status = Status.BLOCKED
            metrics.agents[self.agent_data.id].status = Status.BLOCKED

        tools = self.parse_tools(self.last_response)
        
        # exec tools 
        
        for tool in tools:
            result = self.exec_tools(tool, context_results)
            
            if result is not None:
                yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk=f"\n{result}\n")
