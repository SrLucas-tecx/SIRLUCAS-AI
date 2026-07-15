class DocumentManager:

    def execute(self, data):

        command = data["command"]

        method = getattr(self, command, None)

        if method is None:
            return None

        return method(data)
    