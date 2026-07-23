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

        # ------------------------------
        # Guardar último documento
        # ------------------------------

        if self.current_module == "document":

            self.last_document = self.current_topic

        # ------------------------------
        # Guardar último programa
        # ------------------------------

        elif self.current_module == "system":

            self.last_program = self.current_topic

        # ------------------------------
        # Guardar última búsqueda
        # ------------------------------

        elif self.current_module in ["knowledge", "web"]:

            self.last_search = self.current_topic

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

        return self.last_document

    # ==========================================
    # Último programa
    # ==========================================

    def program(self):

        return self.last_program

    # ==========================================
    # Última búsqueda
    # ==========================================

    def search(self):

        return self.last_search

    # ==========================================
    # ¿Existe documento en contexto?
    # ==========================================

    def has_document(self):

        return self.last_document is not None

    # ==========================================
    # ¿Existe programa en contexto?
    # ==========================================

    def has_program(self):

        return self.last_program is not None

    # ==========================================
    # ¿Existe búsqueda en contexto?
    # ==========================================

    def has_search(self):

        return self.last_search is not None

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