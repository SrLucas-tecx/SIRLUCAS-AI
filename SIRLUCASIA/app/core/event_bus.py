from collections import defaultdict


class EventBus:

    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event, callback):

        if not callable(callback):
            raise ValueError("El callback debe ser una función.")

        self.listeners[event].append(callback)

    def unsubscribe(self, event, callback):

        if event in self.listeners:

            try:
                self.listeners[event].remove(callback)

            except ValueError:
                pass

    def publish(self, event, data=None):

        if event not in self.listeners:
            return

        for callback in list(self.listeners[event]):

            try:
                callback(data)

            except Exception as e:

                listener = getattr(callback, "__self__", None)

                if listener:
                    nombre = listener.__class__.__name__
                else:
                    nombre = callback.__name__

                print(f"[EventBus] Error en {nombre}: {e}")

    def clear(self):
        self.listeners.clear()

    def events(self):
        return list(self.listeners.keys())

    def has_subscribers(self, event):
        return len(self.listeners[event]) > 0