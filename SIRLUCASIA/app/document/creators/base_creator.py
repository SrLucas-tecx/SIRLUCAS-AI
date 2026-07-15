from abc import ABC, abstractmethod


class BaseCreator(ABC):

    @abstractmethod
    def create(self, filepath, content):
        pass
    