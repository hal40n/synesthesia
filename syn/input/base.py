from abc import ABC, abstractmethod

from syn.llm.schema import LLMInput


class InputSource(ABC):
    """
    An InputSource produces the musical observation handed to the LLM.

    Sources capture *what is sounding now*; they never interpret.
    Interpretation belongs to the LLM, governed by /prompts.
    """

    @abstractmethod
    def read(self) -> LLMInput:
        """Return one observation window as an LLMInput."""
