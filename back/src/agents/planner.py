import json
from typing import List
from dataclasses import dataclass
from src.agents.agent import Agent, AgentResponse
from src.core.models import AgentType, AgentsMetrics


@dataclass
class PlannedTask:
    id: str
    description: str
    tool: str
    args: str
    dependencies: List[str]
    estimated_time: int
    status: str = "pending"

class PlannerAgent(Agent):
    def __init__(self):
        system_prompt = """
Tu es l'Architecte Clinique du système C.L.A.R.A.
Ta tâche est de PLANIFIER l'analyse d'un dossier patient de manière STRATÉGIQUE.
... (Règles inchangées) ...
Format JSON attendu :
[
  {
    "id": "step_1",
    "description": "...",
    "tool": "VISION_TOOL",
    "args": "...",
    "dependencies": [],
    "estimated_time": 2
  }
]
"""
        super().__init__(system_prompt, AgentType.PLANNER, model="google/gemma-3-27b-it:free")

    def plan(self, request: str, metrics: AgentsMetrics):
        yield AgentResponse(metrics=metrics, id=self.data.id, chunk="Step 1 : Planification**\n\n")
        prompt = f"Requête à planifier : {request}" 
        full_response = ""
        try:
            for response in self.ask(prompt, metrics):
                full_response += response.chunk
                yield response
        except Exception as e:
            print(f"Erreur lors de la génération du plan : {e}")
            return []
        
        tasks = self._parse_tasks(full_response)
        
        plan_desc = "\n**Plan généré :**\n"
        for t in tasks:
            plan_desc += f"- {t.id}: {t.description} ({t.tool})\n"
        plan_desc += "\n"
        yield AgentResponse(metrics=metrics, id=self.data.id, chunk=plan_desc)
        
        # yield _create_chunk(metrics, executor.data.id, "⚙️ **Phase 2 : Exécution du plan...**\n\n")
        
        # result_dict = executor.execute_plan(tasks, question, metrics)
        # final_answer = result_dict.get('final_answer', "Pas de réponse générée.")
        
        # yield _create_chunk(metrics, executor.data.id, f"**Résultat Final :**\n\n{final_answer}")
            
         

    def _parse_tasks(self, json_response: str) -> List[PlannedTask]:
        try:
            cleaned_response = json_response.replace("```json", "").replace("```", "").strip()
            start = cleaned_response.find("[")
            end = cleaned_response.rfind("]")
            if start != -1 and end != -1:
                cleaned_response = cleaned_response[start:end+1]
                
            data = json.loads(cleaned_response)
            tasks = []
            for item in data:
                task = PlannedTask(
                    id=item.get("id", str(item.get("step", "unknown"))),
                    description=item.get("description", ""),
                    tool=item.get("tool", "NO_TOOL"),
                    args=item.get("args") or item.get("child_prompt", ""),
                    dependencies=item.get("dependencies", []),
                    estimated_time=item.get("estimated_time", 1)
                )
                tasks.append(task)
            return tasks
        except Exception as e:
            print(f"Erreur de parsing du plan : {e}")
            return []