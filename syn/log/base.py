from abc import ABC, abstractmethod
from datetime import datetime


class BaseLogger(ABC):
    def __init__(self):
        self.timestamp = datetime.utcnow().isoformat()

    @abstractmethod
    def write(self, data: dict):
        pass
