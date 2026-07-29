from app.listeners.base_listener import BaseListener
from app.core.logger import Logger



from app.listeners.base_listener import BaseListener
from app.core.logger import Logger, logger


class LoggerListener(BaseListener):

    def __init__(self, use_global=True):
        # Si use_global=True, usa la instancia global
        # Si use_global=False, crea una nueva instancia de Logger
        self.logger = logger if use_global else Logger()

    def handle(self, result):
        self.logger.log(result)