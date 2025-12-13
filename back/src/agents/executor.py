from typing import Dict, List, Any
from src.agents.agent import Agent, AgentResponse
from src.agents.planner import PlannedTask
from src.core.models import AgentType, AgentsMetrics

class ExecutorAgent(Agent):
    def __init__(self):
        system_prompt = """
Tu es l'Exécuteur Clinique du système C.L.A.R.A.
Ta tâche est d'EXÉCUTER les étapes d'un plan médical pré-établi.
Tu as accès aux résultats des étapes précédentes.
Agis avec précision et rigueur médicale.
"""
        super().__init__(system_prompt, AgentType.EXECUTOR, model="google/gemma-3-27b-it:free")
    
    def execute_plan(self, tasks: List[PlannedTask], context: str, global_metrics: AgentsMetrics) -> Dict[str, Any]:
        """
        Exécute un plan complet en respectant les dépendances.
        """
        ordered_tasks = self.topological_sort(tasks)
        
        results = {}
        for task in ordered_tasks:
            if self.dependencies_met(task, results):
                print(f"Executing task: {task.id} - {task.description}")
                result = self.execute_task(task, context, results, global_metrics)
                results[task.id] = result
                task.status = "completed"
            else:
                task.status = "blocked"
                results[task.id] = "BLOCKED: Dependencies not met"
        
        return {
            'tasks': tasks,
            'results': results,
            'final_answer': self.synthesize_results(results)
        }
    
    def topological_sort(self, tasks: List[PlannedTask]) -> List[PlannedTask]:
        sorted_tasks = []
        remaining = tasks.copy()
        
        max_iterations = len(tasks) * 2
        iterations = 0
        
        while remaining and iterations < max_iterations:
            iterations += 1
            progress = False
            for task in remaining:
                if all(dep in [t.id for t in sorted_tasks] for dep in task.dependencies):
                    sorted_tasks.append(task)
                    remaining.remove(task)
                    progress = True
                    break
            
            if not progress:
                sorted_tasks.extend(remaining)
                break
                
        return sorted_tasks
    
    def dependencies_met(self, task: PlannedTask, results: Dict) -> bool:
        return all(dep in results for dep in task.dependencies)
    
    def execute_task(self, task: PlannedTask, context: str, previous_results: Dict, global_metrics: AgentsMetrics) -> str:
        context_prompt = f"Contexte Global : {context}\n"
        if task.dependencies:
            context_prompt += "Résultats précédents :\n"
            for dep in task.dependencies:
                context_prompt += f"- {dep}: {previous_results.get(dep, 'N/A')}\n"

        if task.tool == "VISION_TOOL":
            return f"[VISION] Analyse de {task.args} terminée. Tumeur détectée (simulé)."
        elif task.tool == "GUIDELINE_TOOL":
            return f"[GUIDELINES] Protocoles trouvés pour : {task.args}."
        elif task.tool == "STATS_TOOL":
            return f"[STATS] Données comparatives pour : {task.args}."
        else:
            prompt = f"{context_prompt}\nTâche : {task.description}\nInstruction : Exécute cette tâche."
            
            full_response = ""
            try:
                for response in self.ask(prompt, global_metrics):
                    full_response += response.chunk
                return full_response if full_response else "Error: Empty response."
            except Exception as e:
                return f"Error executing task: {e}"
    
    def synthesize_results(self, results: Dict) -> str:
        synthesis = "Rapport d'exécution du plan :\n"
        for task_id, result in results.items():
            synthesis += f"- {task_id}: {str(result)[:200]}...\n"
        return synthesis