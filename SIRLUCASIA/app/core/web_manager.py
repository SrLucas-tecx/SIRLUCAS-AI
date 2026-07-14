class WebManager:

    def __init__(self):

        print("=" * 50)
        print("[WebManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    def execute(self, data):

        command = data.get("command")

        if command == "search":
            return self.search(data)

        return None

    def search(self, data):

        topic = data.get("topic")

        return f"(WEB) Buscaré información sobre '{topic}'."
    