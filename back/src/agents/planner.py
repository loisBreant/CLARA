from src.agents.agent import Agent, AgentResponse
from src.agents.executor import ExecutorAgent, Tasks
from src.core.models import AgentType, AgentsMetrics



class PlannerAgent(Agent):
    def __init__(self):
        system_prompt = """
Tu es le planner Clinique du système C.L.A.R.A.
Ta tâche est de PLANIFIER l'analyse d'un dossier patient de manière STRATÉGIQUE.
Si il n'y a aucune tache complexe a faire, et seulement une simple question, n'hesite pas a rendre une liste de taches vide et simplement repondre directement.
Format JSON attendu :
[
  {
    "id": "step_1",
    "title": "...",
    "description": "...",
    "dependencies": [],
  }
]
"""
        super().__init__(system_prompt, AgentType.PLANNER)
        self.logs = []

    def plan(self, request: str, metrics: AgentsMetrics):
        yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="Step 1 : Planification**\n\n")
        prompt = f"Requête à planifier : {request}" 
        full_response = ""
        try:
            for response in self.ask(prompt, metrics):
                full_response += response.chunk
                yield response
        except Exception as e:
            print(f"Erreur lors de la génération du plan : {e}")
            return []

        self.logs += full_response
        tasks = Tasks(full_response)
        yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk=tasks.render_tasks())
          
        for t in tasks:
            executor = ExecutorAgent()
            
            full_response = ""
            for response in executor.execute_task(t, tasks, metrics):
                full_response += response
                yield response

            self.logs += full_response
            
        # result_dict = executor.execute_plan(tasks, question, metrics)
        # final_answer = result_dict.get('final_answer', "Pas de réponse générée.")
        
        # yield _create_chunk(metrics, executor.data.id, f"**Résultat Final :**\n\n{final_answer}")
            
         

