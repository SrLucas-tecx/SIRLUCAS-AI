class EventBus:

    def __init__(self):

        self.listeners = {}

    def subscribe(self, event, callback):

        if event not in self.listeners:

            self.listeners[event] = []

        self.listeners[event].append(callback)

    def unsubscribe(self, event, callback):

        if event in self.listeners:

            self.listeners[event].remove(callback)

    def publish(self, event, data=None):

        if event not in self.listeners:

            return

        for callback in self.listeners[event]:

            callback(data)