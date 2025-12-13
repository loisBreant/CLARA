from src.agents.agent import Agent
from src.core.models import AgentType, AgentsMetrics

class ReactiveAgent(Agent):
    def __init__(self):
        system_prompt = "Tu es un assistant médical réactif. Réponds directement et précisément."
        super().__init__(system_prompt, AgentType.REACTIVE, model="google/gemma-3-27b-it:free")
    
    def handle_request(self, request: str, global_metrics: AgentsMetrics) -> str:
        full_response = ""
        try:
            for response in self.ask(request, global_metrics):
                full_response += response.chunk
            return full_response if full_response else "Error: Empty response."
        except Exception as e:
            return f"Error: {e}"
