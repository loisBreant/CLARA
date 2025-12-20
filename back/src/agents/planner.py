from typing import Optional
from src.agents.agent import Agent, AgentResponse
from src.agents.executor import ExecutorAgent
from src.agents.reactive import ReactiveAgent
from src.agents.memory import MemoryAgent
from src.core.models import AgentType, AgentsMetrics, Status
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
- vision_tool(image_path, instruction): Analyse une image selon une instruction précise.
- classification_tool(image_path): Classification d'image (Maligne/Bénigne).
  -> IMPORTANT: Si tu dois enchaîner des calculs (ex: 1+2+3), utilise le format "$step_id" pour faire référence au résultat d'une étape précédente.
  Exemple:
  [
    {"id": "s1", "title": "Calc 1+2", "description": "Utilise add(1, 2)", "dependencies": []},
    {"id": "s2", "title": "Calc s1+3", "description": "Utilise add($s1, 3)", "dependencies": ["s1"]}
  ]

RÈGLES CRITIQUES:
- Chaque tâche doit être exécutable par un agent spécialisé (Executor).
- Sois précis sur les dépendances entre tâches.
- N'utilise les outils QUE SI C'EST NÉCESSAIRE pour répondre à la requête. Si une réponse simple suffit, ne planifie pas d'outil complexe.
- SI LA REQUÊTE EST SIMPLE (ex: "Bonjour", "Merci", question basique sans outil), renvoie une liste vide `[]`. Cela passera directement la main à l'agent Réactif pour répondre.

Format JSON attendu :
[
  {
    "step_id": "step_1",
    "title": "Nom court",
    "description": "Instruction pour l'Executor",
    "dependencies": []
  }
]
"""
        super().__init__(system_prompt, AgentType.PLANNER)
        self.logs = []
        self.chat_history = []

    def plan(self, request: str, metrics: AgentsMetrics, image_url: Optional[str]):
        yield AgentResponse(
            metrics=metrics,
            id=self.agent_data.id,
            chunk="**Phase 1 : Planification Stratégique**\n\n",
        )

        # Format history for context
        history_str = ""
        if self.chat_history:
            history_str = "HISTORIQUE DE LA CONVERSATION PRÉCÉDENTE :\n"
            for msg in self.chat_history:
                role = "Utilisateur" if msg["role"] == "user" else "Assistant"
                history_str += f"- {role}: {msg['content']}\n"
            history_str += "\n"

        prompt = f"{history_str}Nouvelle requête à planifier : {request}"
        if image_url is not None:
            prompt += f"\nUser uploaded image: {image_url}"

        full_response = ""
        try:
            for response in self.ask(prompt, metrics):
                full_response += response.chunk
                yield response
        except Exception as e:
            print(f"Erreur lors de la génération du plan : {e}")
            return []

        tasks = Tasks(full_response, self.agent_data.id)
        memory = MemoryAgent()
        last_agent_id = self.agent_data.id

        if len(tasks) > 0:
            yield AgentResponse(
                metrics=metrics,
                id=self.agent_data.id,
                chunk="\n\n**Phase 2 : Exécution du Plan**\n\n",
            )
            yield AgentResponse(
                metrics=metrics, id=self.agent_data.id, chunk=tasks.render_tasks()
            )

            for t in tasks:
                executor = ExecutorAgent(t, image_url)
                metrics.agents[executor.agent_data.id] = executor.agent_data

                task_result_accumulated = ""
                yield AgentResponse(
                    metrics=metrics,
                    id=executor.agent_data.id,
                    chunk=f"> *Exécution de la tâche : {t.title}*\n",
                )

                for response in executor.execute_task(t, tasks, metrics, memory):
                    task_result_accumulated += response.chunk
                    yield response

                yield AgentResponse(
                    metrics=metrics, id=executor.agent_data.id, chunk="\n\n"
                )
                last_agent_id = executor.agent_data.id
                self.logs.append(task_result_accumulated)

        # Phase 3 : Toujours exécutée, même si pas de tâches (pour réponse simple)
        yield AgentResponse(
            metrics=metrics,
            id=self.agent_data.id,
            chunk="**Phase 3 : Synthèse et Réponse Finale**\n\n",
        )
        reactive = ReactiveAgent()
        reactive.agent_data.dependencies = [last_agent_id]
        metrics.agents[reactive.agent_data.id] = reactive.agent_data

        final_prompt = f"""
Voici le contexte de la demande et les résultats des tâches exécutées.
Synthétise tout cela pour donner une réponse finale complète et claire à l'utilisateur.

CONTEXTE CONVERSATIONNEL (Historique):
{history_str if history_str else "Aucun historique."}

DERNIÈRE REQUÊTE UTILISATEUR:
{request}

RÉSULTATS DES TÂCHES (Outils):
{self.logs if self.logs else "Aucune exécution d'outil."}

PLANIFICATION:
{tasks.render_tasks() if len(tasks) > 0 else "Aucune tâche complexe nécessaire."}
"""

        full_reactive_response = ""
        for response in reactive.ask(final_prompt, metrics):
            full_reactive_response += response.chunk
            yield response

        # Save to history
        self.chat_history.append({"role": "user", "content": request})
        self.chat_history.append(
            {"role": "assistant", "content": full_reactive_response}
        )

        # self.status = Status.FINISHED
        self.agent_data.status = Status.FINISHED
        metrics.agents[self.agent_data.id] = self.agent_data
        yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="")
