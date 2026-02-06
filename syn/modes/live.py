from syn.config import Config
from syn.core.prompt_loader import load_prompt

class LiveMode:
    def __init__(self):
        self.prompt = None

    def start(self):
        self.prompt = load_prompt(Config.PROMPT_LIVE)
        print("[live] mode initialized")
        print(f"[live] prompt loaded ({Config.PROMPT_LIVE})")