from app.database.web_database import WebDatabase


class WebManager:

    def __init__(self):

        self.database = WebDatabase()

        print("=" * 50)
        print("[WebManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # =====================================
    # Dispatcher
    # =====================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe el comando '{command}'."

        return method(data)

    # =====================================
    # Buscar
    # =====================================

    def search(self, data):

        topic = data.get("topic")

        if not topic:
            return "No especificaste qué buscar."

        result = self.database.find(topic)

        if result is None:
            return (
                f"No encontré una búsqueda registrada para '{topic}'."
            )

        return (
            f"Búsqueda web simulada: {result}"
        )