from app.database.conversation_database import ConversationDatabase


# ==================================================
# ConversationManager
# Maneja conversaciones simples
# ==================================================

class ConversationManager:

    def __init__(self):

        self.database = ConversationDatabase()

        print("=" * 50)
        print("[ConversationManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # ==========================================
    # Dispatcher
    # ==========================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe el comando '{command}'."

        return method(data)

    # ==========================================
    # Conversación
    # ==========================================

    def talk(self, data):

        topic = data.get("topic")

        if topic is None:
            return None

        response = self.database.find(topic)

        if response is None:
            return "No tengo una respuesta para eso."

        return response