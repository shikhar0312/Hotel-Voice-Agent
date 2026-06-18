from abc import ABC, abstractmethod

class AbstractSTT(ABC):

    @abstractmethod
    def initialize_stt(self):
        pass
