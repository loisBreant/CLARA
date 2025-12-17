from src.agents.agent import Agent, AgentResponse
from src.agents.executor import ExecutorAgent
from src.agents.memory import MemoryAgent
from src.agents.reactive import ReactiveAgent
from src.core.models import AgentType, AgentsMetrics
from src.core.task import Tasks


class PlannerAgent(Agent):
    def __init__(self):
        system_prompt = """
Tu es le Planner Clinique du système C.L.A.R.A.
Ta mission est de structurer la prise en charge d'une requête médicale complexe en un PLAN D'EXÉCUTION logique et séquentiel.

PROCESSUS:
1. ANALYSE la requête utilisateur.
2. DÉCOMPOSE le problème en tâches unitaires claires.
3. GÉNÈRE la liste COMPLÈTE des tâches au format JSON strict.

CAPACITÉS (Outils disponibles pour l'Executor):
- add(a, b): Additionne 2 nombres.
  Exemple:
  [
    {"id": "s1", "title": "Calc 1+2", "description": "Addition 1 + 2", "dependencies": [], "Var1"},
  ]

RÈGLES CRITIQUES:
- Chaque tâche doit être exécutable par un agent spécialisé (Executor).
- Sois précis sur les dépendances entre tâches.

Format JSON attendu :
[
  {
    "id": "step_1",
    "title": "Nom court",
    "description": "Instruction pour l'Executor",
    "dependencies": []
    "output_variable": "Var1"
  }
]"""
        super().__init__(system_prompt, AgentType.PLANNER)
        self.memory = MemoryAgent()

    def plan(self, request: str, metrics: AgentsMetrics):
        # Create tasks
        yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="**Phase 1 : Planification Stratégique**\n\n")
        prompt = f"Requête à planifier : {request}" 
        full_response = ""
        try:
            for response in self.ask(prompt, metrics):
                full_response += response.chunk
                yield response
        except Exception as e:
            print(f"Erreur lors de la génération du plan : {e}")
            return []

        tasks = Tasks(full_response)
        
        # Execution
        if len(tasks) > 0:
            last_agent_id = self.agent_data.id
            execution_results = {}
            execution_context = f"Requête initiale : {request}\n\nRésultats de l'exécution :\n"
            
            for t in tasks:
                executor = ExecutorAgent()
                executor.agent_data.dependencies = [self.agent_data.id]
                metrics.agents[executor.agent_data.id] = executor.agent_data
                
                task_result_accumulated = ""
                yield AgentResponse(metrics=metrics, id=executor.agent_data.id, chunk=f"> *Exécution de la tâche : {t.title}*\n")
                
                for response in executor.execute_task(t, tasks, metrics, execution_results):
                    task_result_accumulated += response.chunk
                    yield response
                
                execution_results[t.id] = task_result_accumulated
                
                execution_context += f"\n- Tâche '{t.title}' (ID: {t.id}):\n{task_result_accumulated}\n"
                yield AgentResponse(metrics=metrics, id=executor.agent_data.id, chunk="\n\n")
                
                last_agent_id = executor.agent_data.id

            # Phase 3 : Validation & Synthèse
            yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="**Phase 3 : Synthèse et Réponse Finale**\n\n")
            
            reactive = ReactiveAgent()
            reactive.agent_data.dependencies = [last_agent_id]
            metrics.agents[reactive.agent_data.id] = reactive.agent_data
            
            final_prompt = f"""
Voici le contexte de la demande et les résultats des tâches exécutées.
Synthétise tout cela pour donner une réponse finale complète et claire à l'utilisateur.

{execution_context}
"""
            for response in reactive.ask(final_prompt, metrics):
                yield response
