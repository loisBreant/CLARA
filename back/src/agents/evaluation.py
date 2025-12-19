# from typing import List, Dict, Any
# from src.agents.reactive import ReactiveAgent
# from src.agents.planner import PlannerAgent
# from src.agents.executor import ExecutorAgent
# from src.core.models import AgentsMetrics

# class PerformanceMetrics:
#     def __init__(self):
#         self.metrics = {}
    
#     def measure_response_quality(self, response: str) -> Dict[str, float]:
#         return {
#             'length': float(len(response)),
#             'coherence': self.check_coherence(response),
#             'completeness': self.check_completeness(response),
#             'structure': self.check_structure(response)
#         }
    
#     def check_coherence(self, response: str) -> float:
#         connectors = ['et', 'mais', 'or', 'donc', 'car', 'parce que']
#         count = sum(1 for word in connectors if word in response.lower())
#         return min(count / 5.0, 1.0)
    
#     def check_completeness(self, response: str) -> float:
#         aspects = ['introduction', 'détails', 'conclusion']
#         covered = sum(1 for aspect in aspects if aspect in response.lower())
#         return covered / len(aspects)
    
#     def check_structure(self, response: str) -> float:
#         has_lists = '1.' in response or '-' in response
#         has_paragraphs = '\n\n' in response
#         score = 0.5 if has_lists else 0.0
#         score += 0.5 if has_paragraphs else 0.0
#         return score

# class AgentComparator:
#     def __init__(self, reactive_agent: ReactiveAgent, planner: PlannerAgent, executor: ExecutorAgent):
#         self.reactive = reactive_agent
#         self.planner = planner
#         self.executor = executor
#         self.metrics_tool = PerformanceMetrics()
    
#     def compare_responses(self, test_queries: List[str]) -> Dict[str, Any]:
#         results = {}
#         for query in test_queries:
#             # Initialize metrics for this run
#             metrics = AgentsMetrics()

#             # 1. Réponse Réactive
#             reactive_response = self.reactive.handle_request(query, metrics)
            
#             # 2. Réponse Planifiée (Plan + Execute)
#             # Le Planner génère les tâches
#             tasks = self.planner.plan(query, metrics)
#             # L'Executor exécute et synthétise
#             execution_result = self.executor.execute_plan(tasks, query, metrics)
#             planning_response = execution_result.get('final_answer', "")
            
#             # 3. Métriques de qualité
#             reactive_quality = self.metrics_tool.measure_response_quality(reactive_response)
#             planning_quality = self.metrics_tool.measure_response_quality(planning_response)
            
#             results[query] = {
#                 'reactive': {
#                     'response': reactive_response, 
#                     'quality_metrics': reactive_quality,
#                     'execution_metrics': metrics.agents.get(str(self.reactive.agent_data.id))
#                 },
#                 'planning': {
#                     'response': planning_response, 
#                     'quality_metrics': planning_quality,
#                     # Note: metrics.agents will contain planner and executor data mixed
#                     'agents_metrics': metrics.model_dump()
#                 }
#             }
#         return results
