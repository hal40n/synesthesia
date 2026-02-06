from syn.config import Config
from syn.core.prompt_loader import load_prompt
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput

class LiveMode:
    def __init__(self):
        self.prompt = None
        self.client = None

    def start(self):
        self.prompt = load_prompt(Config.PROMPT_LIVE)
        self.client = LLMClient(self.prompt)

        print("[live] mode initialized")
        print(f"[live] prompt loaded ({Config.PROMPT_LIVE})")

        llm_input = LLMInput(
            key="C major",
            pitch_classes=["C", "E", "G"],
            frequencies=[261.6, 329.6, 392.0],
            dynamics="medium",
            density="normal",
        )
        llm_output = self.client.interpret(llm_input)
        print(f"[live] llm output: {llm_output}")