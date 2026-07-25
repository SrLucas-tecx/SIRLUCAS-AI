from app.core.context_stack import ContextStack

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

        module = self.current_module
        topic = self.current_topic

        # ===============================
        # Programas
        # ===============================
        if module == "system" and topic:
            self.current_program = topic
            self.stack.push_program(topic)

        # ===============================
        # Documentos
        # ===============================
        elif module == "document" and topic:
            self.current_document = topic
            self.stack.push_document(topic)

        # ===============================
        # Búsquedas
        # ===============================
        elif module in ("knowledge", "web") and topic:
            self.current_search = topic
            self.stack.push_search(topic)

        # ===============================
        # DEBUG
        # ===============================
        print("\n========== CONTEXT STACK ==========")
        print("Programas :", self.stack.programs)
        print("Documentos:", self.stack.documents)
        print("Búsquedas :", self.stack.searches)
        print("===================================\n")

    # ==========================================
    # Turno actual
    # ==========================================
    def turn(self):
        return self.turn_number

    # ==========================================
    # Tema actual
    # ==========================================
    def topic(self):
        return self.current_topic

    # ==========================================
    # Módulo actual
    # ==========================================
    def module(self):
        return self.current_module

    # ==========================================
    # Comando actual
    # ==========================================
    def command(self):
        return self.current_command

    # ==========================================
    # Último documento
    # ==========================================
    def document(self):
        return self.current_document

    # ==========================================
    # Último programa
    # ==========================================
    def program(self):
        return self.current_program

    # ==========================================
    # Última búsqueda
    # ==========================================
    def search(self):
        return self.current_search

    # ==========================================
    # ¿Existe documento en contexto?
    # ==========================================
    def has_document(self):
        return self.current_document is not None

    # ==========================================
    # ¿Existe programa en contexto?
    # ==========================================
    def has_program(self):
        return self.current_program is not None

    # ==========================================
    # ¿Existe búsqueda en contexto?
    # ==========================================
    def has_search(self):
        return self.current_search is not None

    # ==========================================
    # Reiniciar contexto
    # ==========================================
    def clear(self):
        self.turn_number = 0

        self.current_topic = None
        self.current_module = None
        self.current_command = None

        self.current_document = None
        self.current_program = None
        self.current_search = None

        self.stack = ContextStack()
