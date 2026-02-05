import httpx
from app.config import get_settings


class ModelClient:
    """
    Minimal HTTP client for vLLM OpenAI-compatible endpoint.
    Replace with your deployment details as needed.
    """

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.Client(timeout=30)

    def generate(self, prompt: str) -> str:
        # This follows the OpenAI /v1/chat/completions style used by vLLM.
        payload = {
            "model": self.settings.model_name,
            "messages": [
                {"role": "system", "content": "You are a concise, safety-focused assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 512,
        }
        resp = self.client.post(self.settings.model_server_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        # vLLM returns choices[0].message.content in OpenAI format
        return data["choices"][0]["message"]["content"]

