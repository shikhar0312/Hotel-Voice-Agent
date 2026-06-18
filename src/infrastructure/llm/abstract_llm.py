from abc import ABC, abstractmethod

class AbstractLLM(ABC):

    @abstractmethod
    def initialize_llm(self):
        pass
