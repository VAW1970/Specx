import time
import ollama
from ollama import Client
from typing import Generator


class OllamaClient:
    """Client wrapper around the local Ollama instance with caching."""

    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.client = Client(host=host, timeout=120.0)
        self._models_cache: list[dict] | None = None
        self._models_cache_ts: float = 0
        self._cache_ttl: float = 10.0  # seconds

    def list_models(self, force: bool = False) -> list[dict]:
        """Return available models, with short TTL cache to avoid blocking pages."""
        now = time.monotonic()
        if not force and self._models_cache is not None and (now - self._models_cache_ts) < self._cache_ttl:
            return self._models_cache
        try:
            response = self.client.list()
            models = []
            for m in response.models:
                models.append({
                    "name": m.model,
                    "size": m.size,
                    "modified_at": str(m.modified_at),
                })
            self._models_cache = models
            self._models_cache_ts = now
            return models
        except Exception as e:
            if self._models_cache is not None:
                return self._models_cache  # return stale cache on error
            return [{"name": "error", "size": 0, "modified_at": str(e)}]

    def chat(
        self,
        model: str,
        messages: list[dict],
        system: str | None = None,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Send a chat request to Ollama.

        Returns the full response string when stream=False, or a generator
        of string chunks when stream=True.
        """
        payload: dict = {"model": model, "messages": messages}
        if system:
            payload["system"] = system

        if stream:
            return self._stream_chat(payload)
        else:
            response = self.client.chat(**payload)
            return response["message"]["content"]

    def _stream_chat(self, payload: dict) -> Generator[str, None, None]:
        stream = self.client.chat(**payload, stream=True)
        for chunk in stream:
            content = chunk["message"]["content"]
            if content:
                yield content

    def generate(
        self,
        model: str,
        prompt: str,
        system: str | None = None,
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Send a generate request to Ollama."""
        payload: dict = {"model": model, "prompt": prompt}
        if system:
            payload["system"] = system

        if stream:
            return self._stream_generate(payload)
        else:
            response = self.client.generate(**payload)
            return response["response"]

    def _stream_generate(self, payload: dict) -> Generator[str, None, None]:
        stream = self.client.generate(**payload, stream=True)
        for chunk in stream:
            if chunk["response"]:
                yield chunk["response"]

    def pull_model(self, model_name: str) -> str:
        """Pull a model from the Ollama registry."""
        try:
            self.client.pull(model_name)
            return f"Model '{model_name}' pulled successfully."
        except Exception as e:
            return f"Error pulling model: {e}"
