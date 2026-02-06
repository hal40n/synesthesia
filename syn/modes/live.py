from syn.config import Config
from syn.core.prompt_loader import load_prompt
from syn.llm.client import LLMClient
from syn.llm.schema import LLMInput

class LiveMode:
    def __init__(self):
        self.prompt = None
        self.client = None

    def start(self, session: Session):
        if session.session_name is None:
            print("[live] unnamed session")

        print(f"[live] key={session.key}, session={session.session_name}")
