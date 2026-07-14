import time


class ContextManager:

    def __init__(self):

        self.turn_count = 0
        self.reset()

    def reset(self):

        self.context = {
            "topic": None,
            "module": None,
            "command": None,
            "last_message": None,
            "timestamp": None
        }

    def update(self, data):

        if not isinstance(data, dict):
            return

        self.turn_count += 1

        self.context["topic"] = data.get("key") or data.get("topic")
        self.context["module"] = data.get("module")
        self.context["command"] = data.get("command")
        self.context["last_message"] = data
        self.context["timestamp"] = time.time()

    def get(self):

        return self.context

    def turn(self):

        return self.turn_count

    def topic(self):

        return self.context["topic"]

    def module(self):

        return self.context["module"]

    def command(self):

        return self.context["command"]