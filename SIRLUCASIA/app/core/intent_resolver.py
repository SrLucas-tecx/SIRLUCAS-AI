class IntentResolver:

    def __init__(self):
        pass

    def resolve(self, data):

        if not isinstance(data, dict):
            return data

        module = data.get("module")
        command = data.get("command")

        intent = None

        if module == "system":

            if command == "open":
                intent = "OPEN_PROGRAM"

            elif command == "close":
                intent = "CLOSE_PROGRAM"

        elif module == "document":

            if command == "create":
                intent = "CREATE_DOCUMENT"

            elif command == "write":
                intent = "WRITE_DOCUMENT"

            elif command == "read":
                intent = "READ_DOCUMENT"

            elif command == "delete":
                intent = "DELETE_DOCUMENT"

        elif module == "knowledge":

            intent = "SEARCH_KNOWLEDGE"

        elif module == "web":

            intent = "SEARCH_WEB"

        elif module == "calculator":

            intent = "CALCULATE"

        elif module == "memory":

            if command == "remember":
                intent = "SAVE_MEMORY"

            elif command == "recall":
                intent = "READ_MEMORY"

            elif command == "forget":
                intent = "FORGET_MEMORY"

        elif module == "conversation":

            intent = "CHAT"

        # Si no encontró ninguna intención,
        # marcar como desconocida.
        if intent is None:
            data["module"] = "unknown"
            data["intent"] = "UNKNOWN"
        else:
            data["intent"] = intent

        return data