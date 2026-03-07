from fastapi import FastAPI
import requests

app = FastAPI()

OPENROUTER_KEY = "YOUR_KEY"

@app.get("/ask")
def ask_agent(prompt: str):

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}"
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    return response.json()