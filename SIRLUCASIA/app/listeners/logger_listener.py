from app.core.logger import Logger
from app.listeners.base_listener import BaseListener


class LoggerListener(BaseListener):

    def __init__(self):

        self.logger = Logger()

    def handle(self, result):

        if result.success:

            self.logger.info(

                result.module,

                result.command,

                result.message

            )

        else:

            self.logger.error(

                result.module,

                result.command,

                result.error or result.message

            )