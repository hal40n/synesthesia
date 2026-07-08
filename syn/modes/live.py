from syn.core.prompt_loader import load_prompt
from syn.config import Config
from syn.input.factory import create_input_source
from syn.llm.client import LLMClient
from syn.log.live import LiveLogger


class LiveMode:
    def start(self, session):
        # ---- option validation ----
        if session.seed is not None:
            raise ValueError("[live] --seed is not allowed")

        if session.session_name is None:
            print("[live] unnamed session")

        # ---- init ----
        self.prompt = load_prompt(Config.PROMPT_LIVE)
        self.client = LLMClient(
            self.prompt,
            temperature=Config.LLM_TEMPERATURE_LIVE,
            provider=Config.SYN_LLM_PROVIDER,
            base_url=Config.SYN_LLM_BASE_URL,
            model=Config.SYN_LLM_MODEL,
        )

        print("[live] mode initialized")
        print(f"[live] temperature={Config.LLM_TEMPERATURE_LIVE}")
        print(f"[live] key={session.key}, session={session.session_name}")
        print(f"[live] input source={Config.SYN_INPUT_SOURCE}")

        source = create_input_source(Config.SYN_INPUT_SOURCE, key=session.key)
        llm_input = source.read()

        output = self.client.interpret(llm_input)
        print(f"[live] LLM output: {output}")

        # ---- logging ----
        logger = LiveLogger()
        logger.write({
            "timestamp": logger.timestamp,
            "mode": "live",
            "session": session.session_name,
            "key": session.key,
            "temperature": Config.LLM_TEMPERATURE_LIVE,
            "llm_output": output.__dict__,
        })
