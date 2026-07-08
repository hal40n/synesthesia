import json

import requests

from syn.llm.schema import LLMInput, LLMOutput, validate_output

MAX_ATTEMPTS = 2

PROVIDERS = ("lmstudio", "ollama")

# Worth one retry: network hiccups and malformed LLM output (stochastic
# at temperature > 0). HTTP status errors and response-shape errors are
# deterministic — retrying them only doubles the wait.
RETRYABLE_ERRORS = (requests.ConnectionError, requests.Timeout, ValueError)


class LLMClient:

    def __init__(
        self,
        prompt: str,
        temperature: float = 0.0,
        *,
        provider: str,
        base_url: str,
        model: str,
    ):
        if provider not in PROVIDERS:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        self.prompt = prompt
        self.temperature = temperature
        self.provider = provider
        self.base_url = base_url
        self.model = model

    def interpret(self, llm_input: LLMInput) -> LLMOutput:
        if self.provider == "lmstudio":
            call = self._lmstudio_interpret
        else:
            call = self._ollama_interpret

        first_error = None
        last_error = None
        for _ in range(MAX_ATTEMPTS):
            try:
                return call(llm_input)
            except RETRYABLE_ERRORS as e:
                if first_error is None:
                    first_error = e
                last_error = e
        raise last_error from first_error

    def _lmstudio_interpret(self, llm_input: LLMInput) -> LLMOutput:
        url = f"{self.base_url}/v1/chat/completions"

        messages = [
            { "role": "system", "content": self.prompt },
            { "role": "user", "content": json.dumps(llm_input.__dict__) },
        ]

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "stream": False,
        }

        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return self._parse_output(content)

    def _ollama_interpret(self, llm_input: LLMInput) -> LLMOutput:
        url = f"{self.base_url}/api/chat"

        messages = [
            { "role": "system", "content": self.prompt },
            { "role": "user", "content": json.dumps(llm_input.__dict__) },
        ]

        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }

        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return self._parse_output(content)

    def _parse_output(self, content: str) -> LLMOutput:
        # LLM may return JSON wrapped in markdown code blocks
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM output: {e}\nRaw content: {repr(content)}")

        output = LLMOutput(
            base_hue=float(data["base_hue"]),
            hue_offset=float(data["hue_offset"]),
            saturation=float(data["saturation"]),
            brightness=float(data["brightness"]),
        )
        validate_output(output)
        return output
