from __future__ import annotations

import ollama


class OllamaLLMClient:
    def __init__(self, model: str = "mistral:7b") -> None:
        self.model = model

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict JSON generator. "
                        "Return one valid JSON object only. "
                        "Do not explain. Do not list attractions. "
                        "Do not summarize the dataset."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0.0,
                "top_p": 0.8
            }
        )
        return response["message"]["content"]