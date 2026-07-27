from app.listeners.base_listener import BaseListener
from app.core.logger import Logger


class LoggerListener(BaseListener):

    def __init__(self):

        self.logger = Logger()

    def handle(self, event):

        result = event.get("result")

        self.logger.info(

            module=result.module,

            command=result.command,

            message=result.message

        )