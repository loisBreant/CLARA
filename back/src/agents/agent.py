class Agent:
    def __init__(self, model_id):
        self.client = 
    
    
    def ask_llm(c):
        def guess(client: InferenceClient, model_id: str, question: str) -> str:
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
    )
    return response.choices[0].message.content

        
        pass