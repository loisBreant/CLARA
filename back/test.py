from openrouter import OpenRouter
import os

with OpenRouter(
    api_key=os.getenv("OPEN_ROUTER_API_KEY")
) as client:
    stream = client.chat.send(
        model="google/gemma-3-27b-it:free",
        messages=[{"role": "user", "content": "Write a story"}],
        stream=True
    )
    for event in stream:
        # Full type information for streaming responses
        content = event.choices[0].delta.content if event.choices else None
        print(content, end="", flush=True)

