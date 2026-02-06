from syn.config import Config
from syn.core.prompt_loader import load_prompt

class ResearchMode:
    def __init__(self):
        self.prompt = None

    def start(self):
        self.prompt = load_prompt(Config.PROMPT_RESEARCH)
        print("[research] mode initialized")
        print(f"[research] prompt loaded ({Config.PROMPT_RESEARCH})")