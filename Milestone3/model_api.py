import os
from huggingface_hub import InferenceClient

def query_model(prompt):
    HF_TOKEN = os.getenv("HF_TOKEN")
    client = InferenceClient(
        model="Qwen/Qwen2.5-72B-Instruct",
        token=HF_TOKEN
    )
    response = client.chat_completion(
        messages=[
            {
                "role": "system",
                "content": "You are a certified professional fitness trainer. Provide detailed, structured, day-by-day workout plans."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=2500,
        temperature=0.7
    )
    return response.choices[0].message.content
