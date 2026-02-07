import json
from pathlib import Path
from syn.log.base import BaseLogger
from syn.config import Config


class ResearchLogger(BaseLogger):
    def __init__(self):
        super().__init__()
        self.log_dir = Config.SYN_LOG_RESEARCH_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write(self, data: dict):
        filename = f"{self.timestamp}.json"
        path = self.log_dir / filename

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
