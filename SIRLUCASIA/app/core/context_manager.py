class ContextManager:

    def __init__(self):

        self.reset()

    def reset(self):

        self.context = {
            "topic": None,
            "module": None,
            "command": None,
            "last_message": None
        }

    def update(self, data):

        if not isinstance(data, dict):
            return

        self.context["topic"] = data.get("key")
        self.context["module"] = data.get("module")
        self.context["command"] = data.get("command")
        self.context["last_message"] = data

    def get(self):

        return self.context

    def topic(self):

        return self.context["topic"]

    def module(self):

        return self.context["module"]

    def command(self):

        return self.context["command"]
    