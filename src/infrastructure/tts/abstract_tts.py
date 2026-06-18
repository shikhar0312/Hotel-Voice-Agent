from abc import ABC, abstractmethod

class AbstractTTS(ABC):

    @abstractmethod
    def initialize_tts(self):
        pass
