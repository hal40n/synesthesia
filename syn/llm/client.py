from syn.llm.schema import LLMInput, LLMOutput, validate_output
import os
import requests
import json

class LLMClient:
    
    def __init__(self, prompt: str, temperature: float = 0.0):
        self.prompt = prompt
        self.temperature = temperature
        self.provider = os.getenv("SYN_LLM_PROVIDER", "lmstudio")
        self.base_url = os.getenv("SYN_LLM_BASE_URL", "http://127.0.0.1:1234")
        self.model = os.getenv("SYN_LLM_MODEL", "allura-forge_llama-3.3-8b-instruct")

    def interpret(self, llm_input: LLMInput) -> LLMOutput:
        last_error = None

        for attempt in range(1, 2):
            try:
                if self.provider == "lmstudio":
                    return self._lmstudio_interpret(llm_input)
                elif self.provider == "ollama":
                    return self._ollama_interpret(llm_input)
                else:
                    raise RuntimeError(f"Unsupported LLM provider: {self.provider}")
            except Exception as e:
                last_error = e
                if attempt == 1:
                    continue # retry
                else:
                    raise last_error

        raise last_error

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