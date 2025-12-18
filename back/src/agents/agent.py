from typing import Generator, Optional
from openrouter import OpenRouter
from dotenv import dotenv_values
from openrouter import components
import time
import uuid
from src.agents.telemetrics import append_to_csv
from src.core.models import AgentData, AgentType, AgentsMetrics, AgentResponse, Status

config = dotenv_values(".env")

class Agent:
    def __init__(self, system_prompt: str, agent_type: AgentType,  agent_data: Optional[AgentData] = None, model: str = "google/gemma-3-27b-it:free"):
        self.client = OpenRouter(api_key=config["OPENROUTER_API_KEY"])
        self.model = model
        self.system_prompt = system_prompt
        self.last_response: str = ""
                    
        self.agent_data = agent_data if agent_data else AgentData(
            id=str(uuid.uuid4()),
            type=agent_type,
        )

    def reset_id(self):
        self.agent_data.id = str(uuid.uuid4())

    def update_status(self, new_status: Status, metrics: AgentsMetrics, task = None):
        self.agent_data.status = new_status
        metrics.agents[self.agent_data.id] = self.agent_data
        if task:
            task.status = new_status


    def ask(self, prompt: str, metrics: AgentsMetrics) -> Generator[AgentResponse, None, None]:
        self.last_response = ""
        metrics.agents[self.agent_data.id] = self.agent_data

        base_input_tokens = self.agent_data.input_token_count
        base_output_tokens = self.agent_data.output_token_count
        base_time_taken = self.agent_data.time_taken

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
            request_duration = time.time() - start_time
            
            self.agent_data.time_taken = base_time_taken + request_duration
            
            if event.usage:
                self.agent_data.input_token_count = base_input_tokens + event.usage.prompt_tokens
                self.agent_data.output_token_count = base_output_tokens + event.usage.completion_tokens
                
                metrics.agents[self.agent_data.id] = self.agent_data
                yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk="")
            
                continue

            if not event.choices:
                continue

            chunk: Optional[str] = event.choices[0].delta.content # type:ignore

            if chunk:
                current_output_tokens += 1
                self.agent_data.output_token_count = base_output_tokens + current_output_tokens
                
                metrics.agents[self.agent_data.id] = self.agent_data
                self.last_response += chunk
                yield AgentResponse(metrics=metrics, id=self.agent_data.id, chunk=chunk)

        request_duration = time.time() - start_time
        self.agent_data.time_taken = base_time_taken + request_duration
        metrics.agents[self.agent_data.id] = self.agent_data

        # csv_header = ["timestamp", "model_kind", "model_name", "input_tokens", "output_tokens", "time_taken"]
        append_to_csv(str(self.agent_data.type), self.model, self.agent_data.input_token_count, self.agent_data.output_token_count, self.agent_data.time_taken)
