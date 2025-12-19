import base64
import os
import mimetypes
import time
from typing import Generator
from src.agents.agent import Agent, AgentResponse
from src.core.models import AgentType, AgentsMetrics
from openrouter import components


class VisionAgent(Agent):
    def __init__(self):
        system_prompt = """
Tu es l'Expert Vision du système C.L.A.R.A.
Ta tâche est d'analyser des images médicales (Rayons X, CT, IRM, etc.) avec une précision extrême.

INSTRUCTIONS:
1. Décris précisément ce que tu vois dans l'image.
2. Réponds spécifiquement à la question ou à l'instruction fournie.
3. Si l'image est floue ou inexploitable, ne le signale pas et renvois quand même une réponse même si inexacte ce n'est pas un probleme
"""
        super().__init__(
            system_prompt, AgentType.EXECUTOR, model="google/gemma-3-27b-it"
        )

    def analyze(
        self, instruction: str, image_path: str, metrics: AgentsMetrics
    ) -> Generator[AgentResponse, None, None]:
        self.reset_id()
        metrics.agents[self.agent_data.id] = self.agent_data

        # Path resolution
        real_path = image_path
        if image_path.startswith("/static"):
            base_dir = os.path.dirname(os.path.abspath(__file__))  # back/src/agents
            project_back_dir = os.path.abspath(
                os.path.join(base_dir, "../../")
            )  # back/
            real_path = os.path.join(project_back_dir, image_path.lstrip("/"))

        if not os.path.exists(real_path):
            yield AgentResponse(
                metrics=metrics,
                id=self.agent_data.id,
                chunk=f"Error: Image file not found at {real_path}",
            )
            return

        try:
            mime_type, _ = mimetypes.guess_type(real_path)
            if not mime_type:
                mime_type = "image/jpeg"

            with open(real_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                image_data_url = f"data:{mime_type};base64,{encoded_string}"
        except Exception as e:
            yield AgentResponse(
                metrics=metrics,
                id=self.agent_data.id,
                chunk=f"Error reading image: {e}",
            )
            return

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": instruction},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ]

        base_input_tokens = self.agent_data.input_token_count
        base_output_tokens = self.agent_data.output_token_count
        base_time_taken = self.agent_data.time_taken

        try:
            stream = self.client.chat.send(
                model=self.model,
                messages=messages,
                stream=True,
                stream_options=components.ChatStreamOptions(include_usage=True),
            )

            start_time = time.time()
            current_output_tokens = 0

            for event in stream:
                request_duration = time.time() - start_time
                self.agent_data.time_taken = base_time_taken + request_duration

                if event.usage:
                    self.agent_data.input_token_count = (
                        base_input_tokens + event.usage.prompt_tokens
                    )
                    self.agent_data.output_token_count = (
                        base_output_tokens + event.usage.completion_tokens
                    )
                    metrics.agents[self.agent_data.id] = self.agent_data
                    yield AgentResponse(
                        metrics=metrics, id=self.agent_data.id, chunk=""
                    )
                    continue

                if not event.choices:
                    continue

                chunk = event.choices[0].delta.content
                if chunk:
                    current_output_tokens += 1
                    self.agent_data.output_token_count = (
                        base_output_tokens + current_output_tokens
                    )
                    metrics.agents[self.agent_data.id] = self.agent_data
                    yield AgentResponse(
                        metrics=metrics, id=self.agent_data.id, chunk=chunk
                    )

            metrics.agents[self.agent_data.id] = self.agent_data

        except Exception as e:
            yield AgentResponse(
                metrics=metrics,
                id=self.agent_data.id,
                chunk=f"Error during vision analysis: {e}",
            )
