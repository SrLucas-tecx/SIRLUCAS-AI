from app.listeners.base_listener import BaseListener


class AIListener(BaseListener):

    def __init__(self):

        self.last_event = None

    def handle(self, event):

        self.last_event = event