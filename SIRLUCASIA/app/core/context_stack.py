# ==================================================
# ContextStack
# Guarda el historial de objetos activos
# ==================================================

class ContextStack:

    def __init__(self):

        self.clear()

    # ==================================================
    # Programas
    # ==================================================

    def push_program(self, program):

        if program is None:
            return

        if program in self.programs:
            self.programs.remove(program)

        self.programs.append(program)

    def last_program(self):

        if not self.programs:
            return None

        return self.programs[-1]

    def pop_program(self):

        if not self.programs:
            return None

        return self.programs.pop()

    # ==================================================
    # Documentos
    # ==================================================

    def push_document(self, document):

        if document is None:
            return

        if document in self.documents:
            self.documents.remove(document)

        self.documents.append(document)

    def last_document(self):

        if not self.documents:
            return None

        return self.documents[-1]

    def pop_document(self):

        if not self.documents:
            return None

        return self.documents.pop()

    # ==================================================
    # Búsquedas
    # ==================================================

    def push_search(self, search):

        if search is None:
            return

        if search in self.searches:
            self.searches.remove(search)

        self.searches.append(search)

    def last_search(self):

        if not self.searches:
            return None

        return self.searches[-1]

    def pop_search(self):

        if not self.searches:
            return None

        return self.searches.pop()

    # ==================================================
    # Reiniciar
    # ==================================================

    def clear(self):

        self.programs = []

        self.documents = []

        self.searches = []