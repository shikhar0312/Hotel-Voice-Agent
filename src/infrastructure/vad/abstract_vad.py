from abc import ABC, abstractmethod

class AbstractVAD(ABC):

    @abstractmethod
    def initialize_vad(self):
        pass
