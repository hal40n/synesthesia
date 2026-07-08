from abc import ABC, abstractmethod
from datetime import datetime, timezone


class BaseLogger(ABC):
    def __init__(self):
        # Naive-UTC isoformat: timestamps double as log filenames,
        # so keep the shape free of a "+00:00" offset suffix.
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

    @abstractmethod
    def write(self, data: dict):
        pass
