from pydantic import BaseModel
from typing import Generator, Optional
from openrouter import OpenRouter
from dotenv import dotenv_values
from openrouter import components
import time

config = dotenv_values(".env")


class AgentMetrics(BaseModel):
    input_token_count: float = 0.0
    output_token_count: float = 0.0
    current_time_taken: float = 0.0  # in seconds
    total_time_taken: float = 0.0  # in seconds
    current_input_token_count: float = 0.0  # for the current chat message


class AgentResponse(BaseModel):
    metrics: AgentMetrics
    chunk: str


class Agent:
    def __init__(self, system_prompt: str, model: str = "google/gemma-3-27b-it:free"):
        self.client = OpenRouter(api_key=config["OPENROUTER_API_KEY"])
        self.model = model
        self.system_prompt = system_prompt
        self.metrics = AgentMetrics()

    def ask(self, prompt: str) -> Generator[str, None, None]:
        """
        Yields jsons of AgentResponse
        """
        full_prompt = f"""\
SYSTEM_PROMPT: {self.system_prompt}
---
USER_PROMPT: {prompt}\
"""
        stream = self.client.chat.send(
            model=full_prompt,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            stream_options=components.ChatStreamOptions(include_usage=True),
        )
        start_time = time.time()

        cur_token_count = 0

        for event in stream:
            if event.usage:
                self.metrics.output_token_count += event.usage.completion_tokens
                self.metrics.input_token_count += event.usage.prompt_tokens
                yield (
                    AgentResponse(metrics=self.metrics, chunk="").model_dump_json()
                    + "\n"
                )
                continue

            if not event.choices:
                continue

            chunk: Optional[str] = event.choices[0].delta.content

            if chunk:
                cur_token_count += 1
                self.metrics.current_input_token_count = cur_token_count
                yield (
                    AgentResponse(metrics=self.metrics, chunk=chunk).model_dump_json()
                    + "\n"
                )
            self.metrics.current_input_token_count = 0
            self.metrics.current_time_taken = time.time() - start_time

        self.metrics.total_time_taken += self.metrics.current_time_taken
