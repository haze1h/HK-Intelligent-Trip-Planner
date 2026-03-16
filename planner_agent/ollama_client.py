from __future__ import annotations

import ollama


class OllamaLLMClient:
    def __init__(self, model: str = "qwen3:4b") -> None:
        self.model = model

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0.3
            }
        )
        return response["message"]["content"]