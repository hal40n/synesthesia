from syn.core.prompt_loader import load_prompt
from syn.config import Config
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput
from syn.log.research import ResearchLogger


class ResearchMode:
    def __init__(self):
        self.prompt = None
        self.client = LLMClient(
            prompt=self.prompt,
            temperature=Config.LLM_TEMPERATURE_RESEARCH,
        )

        print(f"[research] temperature={Config.LLM_TEMPERATURE_RESEARCH}")

    def start(self, session):
        # ---- option validation ----
        if session.session_name is not None:
            raise ValueError("[research] --session is not allowed")

        if session.seed is None:
            print("[research] warning: seed not set")

        # ---- init ----
        self.prompt = load_prompt(Config.PROMPT_RESEARCH)
        self.client = LLMClient(self.prompt, temperature=Config.LLM_TEMPERATURE_RESEARCH)

        print("[research] mode initialized")
        print(f"[research] key={session.key}, seed={session.seed}")

        # dummy input (unchanged)
        llm_input = LLMInput(
            key=session.key or "C major",
            pitch_classes=["C", "E", "G"],
            frequencies=[261.6, 329.6, 392.0],
            dynamics="medium",
            density="normal",
        )

        output = self.client.interpret(llm_input)
        print(f"[research] LLM output: {output}")

        # ---- logging ----
        logger = ResearchLogger()
        logger.write({
            "timestamp": logger.timestamp,
            "mode": "research",
            "key": session.key,
            "seed": session.seed,
            "temperature": Config.LLM_TEMPERATURE_RESEARCH,
            "llm_input": llm_input.__dict__,
            "llm_output": output.__dict__,
        })
