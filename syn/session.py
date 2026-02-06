from syn.modes.research import ResearchMode
from syn.modes.live import LiveMode

class Session:
    def __init__(self, mode: str):
        self.mode_name = mode
        self.mode = self._create_mode(mode)

    def _create_mode(self, mode: str):
        if mode == "research":
            return ResearchMode()
        elif mode == "live":
            return LiveMode()
        else:
            raise ValueError(f"Invalid mode: {mode}")

    def start(self):
        self.mode.start()