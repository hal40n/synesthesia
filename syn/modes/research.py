from syn.core.prompt_loader import load_prompt
from syn.config import Config
from syn.input.factory import create_input_source
from syn.llm.client import LLMClient
from syn.log.research import ResearchLogger


class ResearchMode:
    def start(self, session):
        # ---- option validation ----
        if session.session_name is not None:
            raise ValueError("[research] --session is not allowed")

        if session.seed is None:
            print("[research] warning: seed not set")

        # ---- init ----
        self.prompt = load_prompt(Config.PROMPT_RESEARCH)
        self.client = LLMClient(
            self.prompt,
            temperature=Config.LLM_TEMPERATURE_RESEARCH,
            provider=Config.SYN_LLM_PROVIDER,
            base_url=Config.SYN_LLM_BASE_URL,
            model=Config.SYN_LLM_MODEL,
        )

        print("[research] mode initialized")
        print(f"[research] temperature={Config.LLM_TEMPERATURE_RESEARCH}")
        print(f"[research] key={session.key}, seed={session.seed}")
        print(f"[research] input source={Config.SYN_INPUT_SOURCE}")

        source = create_input_source(Config.SYN_INPUT_SOURCE, key=session.key)
        llm_input = source.read()

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
