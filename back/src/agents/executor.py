from dataclasses import dataclass
from typing import Dict, List
from src.agents.agent import Agent
from src.core.models import AgentType, AgentsMetrics, Status
from src.core.task import Tasks, PlannedTask
import json


@dataclass
class ToolExecutor:
    function_name: str
    args: list[str]


class ExecutorAgent(Agent):
    def __init__(self):
        system_prompt = """

Role: System 
Tu es l'Exécuteur Clinique du système C.L.A.R.A.
Ta tâche est d'EXÉCUTER les étapes d'un plan médical pré-établi.
Tu as accès aux résultats des étapes précédentes.
Agis avec précision et rigueur médicale.

Voici les tools mis a ta disposition:

---
    OUTIL 1 : "vision_tool"
    DESCRIPTION : Analyse une image mammographique, détecte les masses et renvoie une description.
    QUAND L'UTILISER : Dès que la tâche parle d'image, de radio, de scan ou de vision.
    PARAMÈTRES : {"image_path": "string"}
    ---
    OUTIL 2 : "duckdb_tool"
    DESCRIPTION : Interroge la base de données statistique des cancers (Wisconsin Dataset).
    QUAND L'UTILISER : Quand on demande des moyennes, des comparaisons ou des stats.
    PARAMÈTRES : {"sql_query": "string"}
    ---
    OUTIL 3 : "rag_tool"
    DESCRIPTION : Cherche dans les documents PDF de référence (Guidelines).
    QUAND L'UTILISER : Pour vérifier un protocole ou une contre-indication.
    PARAMÈTRES : {"search_query": "string"}
    ---

"""
        super().__init__(system_prompt, AgentType.EXECUTOR, model="google/gemma-3-27b-it:free")

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
                    args=item.get("args", ""),
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Failed to parse json : {e}")
            return []

    def exec_tools(self, tools: ToolExecutor) :
        pass

    def execute_task(self, task: PlannedTask, tasks: Tasks, metrics: AgentsMetrics):
        """
        Exécute un plan complet en respectant les dépendances.
        """

         # check we can exec task
        if tasks.dependencies_met(task):
            metrics.agents[self.agent_data.id].status = Status.PENDING
            task.status = Status.PENDING
            for response in self.ask(task.description, metrics):
                yield response

            metrics.agents[self.agent_data.id].status = Status.FINISHED
            task.status = Status.FINISHED
        else:
            task.status = Status.BLOCKED
            metrics.agents[self.agent_data.id].status = Status.BLOCKED

        tools = self.parse_tools(self.last_response)
        


        # prompt = f"{context_prompt}\nTâche : {task.description}\nInstruction : Exécute cette tâche."

        # try:
        #     for response in self.ask(prompt, global_metrics):
        #     return full_response if full_response else "Error: Empty response."
        # except Exception as e:
        #     return f"Error executing task: {e}"

    def synthesize_results(self, results: Dict) -> str:
        synthesis = "Rapport d'exécution du plan :\n"
        for task_id, result in results.items():
            synthesis += f"- {task_id}: {str(result)[:200]}...\n"
        return synthesis
