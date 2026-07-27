from app.listeners.base_listener import BaseListener


class HistoryListener(BaseListener):

    def __init__(self, history):

        self.history = history

    def handle(self, result):

        self.history.add(

            module=result.module,

            command=result.command,

            topic=result.data

        )