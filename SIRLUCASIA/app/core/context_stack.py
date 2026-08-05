# ==================================================
# ContextStack
# Guarda el historial de objetos activos
# ==================================================

class ContextStack:

    def __init__(self, max_size=10):
        self.max_size = max_size
        self.clear()

    # ==================================================
    # Métodos internos genéricos
    # ==================================================
    def _push(self, stack, value):
        if value is None:
            return
        if value in stack:
            stack.remove(value)
        stack.append(value)
        if len(stack) > self.max_size:
            stack.pop(0)

    def _peek(self, stack):
        if not stack:
            return None
        return stack[-1]

    def _pop(self, stack):
        if not stack:
            return None
        return stack.pop()

    # ==================================================
    # Programas
    # ==================================================
    def push_program(self, program): self._push(self.programs, program)
    def last_program(self): return self.peek_program()
    def peek_program(self): return self._peek(self.programs)
    def pop_program(self): return self._pop(self.programs)

    # ==================================================
    # Documentos
    # ==================================================
    def push_document(self, document): self._push(self.documents, document)
    def last_document(self): return self.peek_document()
    def peek_document(self): return self._peek(self.documents)
    def pop_document(self): return self._pop(self.documents)

    # ==================================================
    # Búsquedas
    # ==================================================
    def push_search(self, search): self._push(self.searches, search)
    def last_search(self): return self.peek_search()
    def peek_search(self): return self._peek(self.searches)
    def pop_search(self): return self._pop(self.searches)

    # ==================================================
    # Entidades
    # ==================================================
    def push_entity(self, entity): self._push(self.entities, entity)
    def last_entity(self): return self.peek_entity()
    def peek_entity(self): return self._peek(self.entities)
    def pop_entity(self): return self._pop(self.entities)

    # ==================================================
    # Personas
    # ==================================================
    def push_person(self, person): self._push(self.persons, person)
    def last_person(self): return self.peek_person()
    def peek_person(self): return self._peek(self.persons)
    def pop_person(self): return self._pop(self.persons)

    # ==================================================
    # Archivos
    # ==================================================
    def push_file(self, file): self._push(self.files, file)
    def last_file(self): return self.peek_file()
    def peek_file(self): return self._peek(self.files)
    def pop_file(self): return self._pop(self.files)

    # ==================================================
    # Carpetas
    # ==================================================
    def push_folder(self, folder): self._push(self.folders, folder)
    def last_folder(self): return self.peek_folder()
    def peek_folder(self): return self._peek(self.folders)
    def pop_folder(self): return self._pop(self.folders)

    # ==================================================
    # URLs
    # ==================================================
    def push_url(self, url): self._push(self.urls, url)
    def last_url(self): return self.peek_url()
    def peek_url(self): return self._peek(self.urls)
    def pop_url(self): return self._pop(self.urls)

    # ==================================================
    # Tareas
    # ==================================================
    def push_task(self, task): self._push(self.tasks, task)
    def last_task(self): return self.peek_task()
    def peek_task(self): return self._peek(self.tasks)
    def pop_task(self): return self._pop(self.tasks)

    # ==================================================
    # Métodos generales
    # ==================================================
    def exists(self, stack_name, value):
        stack = getattr(self, stack_name, None)
        return stack is not None and value in stack

    def contains(self, stack_name, value):
        return self.exists(stack_name, value)

    def count(self, stack_name):
        stack = getattr(self, stack_name, None)
        return len(stack) if stack is not None else 0

    def clear_stack(self, stack_name):
        stack = getattr(self, stack_name, None)
        if stack is not None:
            stack.clear()

    # ==================================================
    # Reiniciar
    # ==================================================
    def clear(self):
        self.programs = []
        self.documents = []
        self.searches = []
        self.entities = []
        self.persons = []
        self.files = []
        self.folders = []
        self.urls = []
        self.tasks = []

    # ==================================================
    # Último elemento global
    # ==================================================
    def last(self):
        stacks = {
            "program": self.programs,
            "document": self.documents,
            "search": self.searches,
            "entity": self.entities,
            "person": self.persons,
            "file": self.files,
            "folder": self.folders,
            "url": self.urls,
            "task": self.tasks
        }
        for stack_type, stack in stacks.items():
            if stack:
                return {"type": stack_type, "value": stack[-1]}
        return None

    # ==================================================
    # Peek de todas las pilas
    # ==================================================
    def peek_all(self):
        return {
            "program": self.peek_program(),
            "document": self.peek_document(),
            "search": self.peek_search(),
            "entity": self.peek_entity(),
            "person": self.peek_person(),
            "file": self.peek_file(),
            "folder": self.peek_folder(),
            "url": self.peek_url(),
            "task": self.peek_task()
        }

    # ==================================================
    # Exportar / Importar
    # ==================================================
    def to_dict(self):
        return {
            "max_size": self.max_size,
            "programs": self.programs,
            "documents": self.documents,
            "searches": self.searches,
            "entities": self.entities,
            "persons": self.persons,
            "files": self.files,
            "folders": self.folders,
            "urls": self.urls,
            "tasks": self.tasks
        }

    def from_dict(self, data):
        self.max_size = data.get("max_size", 10)
        self.programs = data.get("programs", [])
        self.documents = data.get("documents", [])
        self.searches = data.get("searches", [])
        self.entities = data.get("entities", [])
        self.persons = data.get("persons", [])
        self.files = data.get("files", [])
        self.folders = data.get("folders", [])
        self.urls = data.get("urls", [])
        self.tasks = data.get("tasks", [])

    # ==================================================
    # Estadísticas
    # ==================================================
    def statistics(self):
        stats = {
            "total_items": sum([
                len(self.programs),
                len(self.documents),
                len(self.searches),
                len(self.entities),
                len(self.persons),
                len(self.files),
                len(self.folders),
                len(self.urls),
                len(self.tasks)
            ]),
            "stack_count": 9,
            "max_size": self.max_size,
            "programs": len(self.programs),
            "documents": len(self.documents),
            "searches": len(self.searches),
            "entities": len(self.entities),
            "persons": len(self.persons),
            "files": len(self.files),
            "folders": len(self.folders),
            "urls": len(self.urls),
            "tasks": len(self.tasks)
        }
        return stats

    # ==================================================
    # Representación
    # ==================================================
    def __repr__(self):
        return f"<ContextStack stacks=9 total_items={self.statistics()['total_items']} max_size={self.max_size}>"
