from typing import Generator, Iterable, Iterator
from openrouter import OpenRouter
import os
from dotenv import dotenv_values
from openrouter.types.basemodel import Unset

config = dotenv_values(".env")

class Agent:
    def __init__(self, system_prompt:str, model: str="google/gemma-3-27b-it:free"):
        self.client = OpenRouter(api_key=config["OPENROUTER_API_KEY"])
        self.model = model
        self.system_prompt = system_prompt 

    def ask(self, prompt: str) -> Generator[str, None, None]:
        stream = self.client.chat.send(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for event in stream:
            content:Optional[str] = event.choices[0].delta.content if event.choices else None # type:ignore
            if content is None: 
                continue
            yield content

