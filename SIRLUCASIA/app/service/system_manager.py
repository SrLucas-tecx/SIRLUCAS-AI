class SystemManager:

    def execute(self, data):

        command = data.get("command")

        if command == "open":

            app = data.get("app")

            return f"Abriré {app}."

        if command == "close":

            app = data.get("app")

            return f"Cerraré {app}."

        return None
    