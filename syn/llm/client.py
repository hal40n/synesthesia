from syn.llm.schema import LLMInput, LLMOutput, validate_output
import os

class LLMClient:
    
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.provider = os.getenv("SYN_LLM_PROVIDER", "local")
        self.model = os.getenv("SYN_LLM_MODEL", "placeholder")

    def interpret(self, llm_input: LLMInput) -> LLMOutput:
        if self.provider == "local":
            return self._local_dummy(llm_input)
        else:
            raise RuntimeError(f"Unsupported LLM provider: {self.provider}")

    def _local_dummy(self, llm_input: LLMInput) -> LLMOutput:
        return LLMOutput(
            base_hue=0.0,
            hue_offset=0.0,
            saturation=0.5,
            brightness=0.5
        )

        validate_output(output)
        return output