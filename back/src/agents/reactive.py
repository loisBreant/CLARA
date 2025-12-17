from src.agents.agent import Agent
from src.core.models import AgentType, AgentsMetrics

class ReactiveAgent(Agent):
    def __init__(self):
        system_prompt = f"""\
Tu es l'Interface Clinique C.L.A.R.A (Reactive Agent).
Ton rôle est de synthétiser les résultats de l'exécution du plan pour fournir une RÉPONSE FINALE cohérente et professionnelle à l'utilisateur.

CONTEXTE:
Tu recevras l'historique de ce qui a été planifié et exécuté (résultats des outils, analyses intermédiaires).

TA MISSION:
1. Assemble les informations recueillies.
2. Réponds à la question initiale de l'utilisateur.
3. Adopte un ton médical, empathique mais objectif.
4. Mentionne les éléments clés trouvés (ex: "L'analyse d'image a révélé...", "Selon les guidelines...").
5. Ne mentionne pas les autres agents produit une reponse de la meilleure qualite possible
"""
        super().__init__(system_prompt, AgentType.REACTIVE, model="google/gemma-3-27b-it:free")
    
    def handle_request(self, request: str, metrics: AgentsMetrics) -> str:
        full_response = ""
        try:
            for response in self.ask(request, metrics):
                full_response += response.chunk
            return full_response if full_response else "Error: Empty response."
        except Exception as e:
            return f"Error: {e}"
