from syn.config import Config
from syn.core.prompt_loader import load_prompt
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput

class ResearchMode:
    def __init__(self):
        self.prompt = None
        self.client = None

    def start(self, session: str):
        if session.seed is None:
            print("[research] warning: seed not set")
        print(f"[research] key={session.key}, seed={session.seed}")
