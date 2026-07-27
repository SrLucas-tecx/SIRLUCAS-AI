from abc import ABC, abstractmethod


class BaseListener(ABC):

    @abstractmethod
    def handle(self, event):

        pass