from syn.llm.schema import LLMInput, LLMOutput, validate_output

class LLMClient:
    
    def __init__(self, prompt: str):
        self.prompt = prompt

    def interpret(self, llm_input: LLMInput) -> LLMOutput:
        output = LLMOutput(
            base_hue=0.0,
            hue_offset=0.0,
            saturation=0.5,
            brightness=0.5
        )

        validate_output(output)
        return output