# ==================================================
# ContextManager
# Guarda el contexto de la conversación
# ==================================================

class ContextManager:

    def __init__(self):

        self.clear()

    # ==========================================
    # Actualizar contexto
    # ==========================================

    def update(self, data):

        self.turn_number += 1

        self.current_topic = data.get("topic")
        self.current_module = data.get("module")
        self.current_command = data.get("command")

        if self.current_module == "document":

            self.last_document = self.current_topic

        elif self.current_module == "system":

            self.last_program = self.current_topic

        elif self.current_module in ("knowledge", "web"):

            self.last_search = self.current_topic

    # ==========================================
    # Getters
    # ==========================================

    def turn(self):
        return self.turn_number

    def topic(self):
        return self.current_topic

    def module(self):
        return self.current_module

    def command(self):
        return self.current_command

    def document(self):
        return self.last_document

    def program(self):
        return self.last_program

    def search(self):
        return self.last_search

    # ==========================================
    # Reiniciar contexto
    # ==========================================

    def clear(self):

        self.turn_number = 0

        self.current_topic = None
        self.current_module = None
        self.current_command = None

        self.last_document = None
        self.last_program = None
        self.last_search = None