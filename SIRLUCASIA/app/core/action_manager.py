class ActionManager:

    def __init__(self):

        self.actions = {}

    def register(self, name, service):

        self.actions[name] = service

    def execute(self, data):

        module = data.get("module")

        service = self.actions.get(module)

        if service is None:
            return None

        return service.execute(data)
    