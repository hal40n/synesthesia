from syn.core.prompt_loader import load_prompt
from syn.config import Config
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput


class LiveMode:
    def __init__(self):
        self.prompt = None
        self.client = LLMClient(
            prompt=self.prompt,
            temperature=Config.LLM_TEMPERATURE_LIVE,
        )

        print(f"[live] temperature={Config.LLM_TEMPERATURE_LIVE}")

    def start(self, session):
        # ---- option validation ----
        if session.seed is not None:
            raise ValueError("[live] --seed is not allowed")

        if session.session_name is None:
            print("[live] unnamed session")

        # ---- init ----
        self.prompt = load_prompt(Config.PROMPT_LIVE)
        self.client = LLMClient(self.prompt, temperature=Config.LLM_TEMPERATURE_LIVE)

        print("[live] mode initialized")
        print(f"[live] key={session.key}, session={session.session_name}")

        llm_input = LLMInput(
            key=session.key or "C major",
            pitch_classes=["C", "E", "G"],
            frequencies=[261.6, 329.6, 392.0],
            dynamics="medium",
            density="normal",
        )

        output = self.client.interpret(llm_input)
        print(f"[live] LLM output: {output}")
