from typing import Generator, Optional, Dict
from openrouter import OpenRouter
from dotenv import dotenv_values
from openrouter import components
import time
import uuid
from src.core.models import AgentData, AgentType, AgentsMetrics, AgentResponse
from pydantic import BaseModel
from uuid import UUID

config = dotenv_values(".env")

class Agent:
    def __init__(self, system_prompt: str, agent_type: AgentType, model: str = "google/gemma-3-27b-it:free"):
        self.client = OpenRouter(api_key=config["OPENROUTER_API_KEY"])
        self.model = model
        self.system_prompt = system_prompt
        
        self.data = AgentData(
            id=uuid.uuid4(),
            type=agent_type
        )

    def ask(self, prompt: str, metrics: AgentsMetrics) -> Generator[AgentResponse, None, None]:
        metrics.agents[self.data.id] = self.data

        # Store baseline values to accumulate
        base_input_tokens = self.data.input_token_count
        base_output_tokens = self.data.output_token_count
        base_time_taken = self.data.time_taken

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        stream = self.client.chat.send(
            model=self.model,
            messages=messages,
            stream=True,
            stream_options=components.ChatStreamOptions(include_usage=True),
        )
        
        start_time = time.time()
        current_output_tokens = 0

        for event in stream:
            # Calculate duration for this specific request
            request_duration = time.time() - start_time
            
            # Update cumulative time
            self.data.time_taken = base_time_taken + request_duration
            
            if event.usage:
                # Update with precise usage data
                self.data.input_token_count = base_input_tokens + event.usage.prompt_tokens
                self.data.output_token_count = base_output_tokens + event.usage.completion_tokens
                
                metrics.agents[self.data.id] = self.data
                yield AgentResponse(metrics=metrics, id=self.data.id, chunk="")
                continue

            if not event.choices:
                continue

            chunk: Optional[str] = event.choices[0].delta.content # type:ignore

            if chunk:
                current_output_tokens += 1
                # Update with estimated output tokens (added to base)
                self.data.output_token_count = base_output_tokens + current_output_tokens
                
                metrics.agents[self.data.id] = self.data
                yield AgentResponse(metrics=metrics, id=self.data.id, chunk=chunk)

        # Final time update
        request_duration = time.time() - start_time
        self.data.time_taken = base_time_taken + request_duration
        metrics.agents[self.data.id] = self.data
