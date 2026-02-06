from syn.config import Config
from syn.core.prompt_loader import load_prompt
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput

class ResearchMode:
    def __init__(self):
        self.prompt = None
        self.client = None

    def start(self):
        self.prompt = load_prompt(Config.PROMPT_RESEARCH)
        self.client = LLMClient(self.prompt)

        print("[research] mode initialized")
        print(f"[research] prompt loaded ({Config.PROMPT_RESEARCH})")

        llm_input = LLMInput(
            key="C major",
            pitch_classes=["C", "D", "E", "F", "G", "A", "B"],
            frequencies=[261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88],
            dynamics="medium",
            density="normal"
        )
        llm_output = self.client.interpret(llm_input)
        print(f"[research] llm output: {llm_output}")