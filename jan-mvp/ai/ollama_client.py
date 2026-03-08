"""
Ollama Client

Handles communication with the local Ollama LLM API.
"""
import requests
from typing import Optional

def generate(prompt: str, model: str = "llama3") -> Optional[str]:
    """
    Calls the local Ollama API to generate text based on a prompt.
    
    Args:
        prompt: The input text prompt.
        model: The local model to use (default: llama3).
        
    Returns:
        The generated text string, or None if the request fails.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response")
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return None
