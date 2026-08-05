from collections import deque
from datetime import datetime

# ==================================================
# ContextStack
# Estructura de pilas (stacks) de corto plazo.
#
# Almacena el historial reciente de distintos tipos de
# contexto manejados por SIRLUCAS AI:
#
#   - programas
#   - documentos
#   - busquedas
#   - entidades
#   - archivos
#   - carpetas
#   - urls
#   - personas
#   - tareas
#
# Cada pila conserva únicamente los últimos N elementos
# (por defecto 10). Al superar el límite, el elemento más
# antiguo se descarta automáticamente gracias a
# collections.deque(maxlen=...).
#
# Cada elemento se guarda como:
#   {"value": <valor>, "timestamp": <ISO 8601>}
#
# Esto permite reconstruir "cuándo" se tocó por última vez
# cada tipo de contexto, algo que ContextManager utiliza
# para resolver referencias (pronombres) como "ábrelo".
# ==================================================

DEFAULT_MAX_SIZE = 10

# Nombre interno de cada pila -> nombre público (para to_dict/estadísticas)
_STACK_NAMES = (
    "programs",
    "documents",
    "searches",
    "entities",
    "files",
    "folders",
    "urls",
    "persons",
    "tasks",
)


class ContextStack:
    """
    Pilas de contexto de corto plazo del asistente.

    No guarda memoria permanente: vive únicamente durante la
    conversación actual y se reinicia junto con el ContextManager.
    """

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self.max_size = max_size
        self._init_stacks()

    # ==========================================
    # Inicialización / reinicio de las pilas
    # ==========================================
    def _init_stacks(self):
        self._programs  = deque(maxlen=self.max_size)
        self._documents = deque(maxlen=self.max_size)
        self._searches  = deque(maxlen=self.max_size)
        self._entities  = deque(maxlen=self.max_size)
        self._files     = deque(maxlen=self.max_size)
        self._folders   = deque(maxlen=self.max_size)
        self._urls      = deque(maxlen=self.max_size)
        self._persons   = deque(maxlen=self.max_size)
        self._tasks     = deque(maxlen=self.max_size)

    def clear(self):
        """Vacía todas las pilas."""
        self._init_stacks()

    # ==========================================
    # Operaciones genéricas internas
    # ==========================================
    def _push(self, stack: deque, value):
        if value is None:
            return None
        # eliminar duplicados previos
        stack = deque([item for item in stack if item["value"] != value], maxlen=self.max_size)
        stack.append({"value": value, "timestamp": datetime.now().isoformat()})
        setattr(self, stack_name, stack)
        return value


    def _pop(self, stack: deque):
        if not stack:
            return None
        return stack.pop()["value"]

    def _peek(self, stack: deque):
        if not stack:
            return None
        return stack[-1]["value"]

    def _values(self, stack: deque):
        return [item["value"] for item in stack]

    # ==========================================
    # Propiedades de solo lectura (compatibilidad
    # con el ContextManager original: .programs,
    # .documents, .searches, etc.)
    # ==========================================
    @property
    def programs(self):
        return self._values(self._programs)

    @property
    def documents(self):
        return self._values(self._documents)

    @property
    def searches(self):
        return self._values(self._searches)

    @property
    def entities(self):
        return self._values(self._entities)

    @property
    def files(self):
        return self._values(self._files)

    @property
    def folders(self):
        return self._values(self._folders)

    @property
    def urls(self):
        return self._values(self._urls)

    @property
    def persons(self):
        return self._values(self._persons)

    @property
    def tasks(self):
        return self._values(self._tasks)

    # ==========================================
    # PUSH
    # ==========================================
    def push_program(self, value):
        return self._push(self._programs, value)

    def push_document(self, value):
        return self._push(self._documents, value)

    def push_search(self, value):
        return self._push(self._searches, value)

    def push_entity(self, value):
        return self._push(self._entities, value)

    def push_file(self, value):
        return self._push(self._files, value)

    def push_folder(self, value):
        return self._push(self._folders, value)

    def push_url(self, value):
        return self._push(self._urls, value)

    def push_person(self, value):
        return self._push(self._persons, value)

    def push_task(self, value):
        return self._push(self._tasks, value)

    # ==========================================
    # POP
    # ==========================================
    def pop_program(self):
        return self._pop(self._programs)

    def pop_document(self):
        return self._pop(self._documents)

    def pop_search(self):
        return self._pop(self._searches)

    def pop_entity(self):
        return self._pop(self._entities)

    def pop_file(self):
        return self._pop(self._files)

    def pop_folder(self):
        return self._pop(self._folders)

    def pop_url(self):
        return self._pop(self._urls)

    def pop_person(self):
        return self._pop(self._persons)

    def pop_task(self):
        return self._pop(self._tasks)

    # ==========================================
    # PEEK (ver el tope sin sacarlo)
    # ==========================================
    def peek_program(self):
        return self._peek(self._programs)

    def peek_document(self):
        return self._peek(self._documents)

    def peek_search(self):
        return self._peek(self._searches)

    def peek_entity(self):
        return self._peek(self._entities)

    def peek_file(self):
        return self._peek(self._files)

    def peek_folder(self):
        return self._peek(self._folders)

    def peek_url(self):
        return self._peek(self._urls)

    def peek_person(self):
        return self._peek(self._persons)

    def peek_task(self):
        return self._peek(self._tasks)

    # ==========================================
    # Estadísticas
    # ==========================================
    def statistics(self):
        return {
            "programs": len(self._programs),
            "documents": len(self._documents),
            "searches": len(self._searches),
            "entities": len(self._entities),
            "files": len(self._files),
            "folders": len(self._folders),
            "urls": len(self._urls),
            "persons": len(self._persons),
            "tasks": len(self._tasks),
            "max_size": self.max_size,
        }

    # ==========================================
    # Serialización
    # ==========================================
    def to_dict(self):
        internal = {
            "programs": self._programs,
            "documents": self._documents,
            "searches": self._searches,
            "entities": self._entities,
            "files": self._files,
            "folders": self._folders,
            "urls": self._urls,
            "persons": self._persons,
            "tasks": self._tasks,
        }
        return {name: list(stack) for name, stack in internal.items()}

    def from_dict(self, data: dict):
        """
        Reconstruye las pilas a partir de un diccionario generado
        previamente por to_dict(). Los elementos deben tener la forma
        {"value": ..., "timestamp": ...}.
        """
        if not data:
            return self

        self._init_stacks()

        mapping = {
            "programs": self._programs,
            "documents": self._documents,
            "searches": self._searches,
            "entities": self._entities,
            "files": self._files,
            "folders": self._folders,
            "urls": self._urls,
            "persons": self._persons,
            "tasks": self._tasks,
        }

        for name, stack in mapping.items():
            for item in data.get(name, []):
                if isinstance(item, dict) and "value" in item:
                    stack.append(item)
                else:
                    # Compatibilidad con listas simples de valores
                    stack.append({
                        "value": item,
                        "timestamp": datetime.now().isoformat(),
                    })

        return self

    def __repr__(self):
        return (f"<ContextStack size={len(self)} max_size={self.max_size} "
                f"program={self.peek_program()} document={self.peek_document()} "
                f"entity={self.peek_entity()} task={self.peek_task()} "
                f"last_access={self.get_last_timestamp('programs')}>")


    def last(self):
        stacks = [
            self._programs,
            self._documents,
            self._searches,
            self._entities,
            self._files,
            self._folders,
            self._urls,
            self._persons,
            self._tasks,
        ]

        for stack in stacks:
            if stack:
                return stack[-1]

        return None
    def exists(self, stack_name, value):
        stack = getattr(self, f"_{stack_name}", None)

        if stack is None:
            return False

        return any(item["value"] == value for item in stack)
    def count(self, stack_name):
        stack = getattr(self, f"_{stack_name}", None)

        if stack is None:
            return 0

        return len(stack)
    def clear_stack(self, stack_name):
        stack = getattr(self, f"_{stack_name}", None)

        if stack is not None:
            stack.clear()
    def peek_all(self):
        return {
            "program": self.peek_program(),
            "document": self.peek_document(),
            "search": self.peek_search(),
            "entity": self.peek_entity(),
            "file": self.peek_file(),
            "folder": self.peek_folder(),
            "url": self.peek_url(),
            "person": self.peek_person(),
            "task": self.peek_task()
        }
    def __len__(self):
        return sum(len(getattr(self, f"_{name}")) for name in _STACK_NAMES)

    def is_empty(self):
        return len(self) == 0

    def get_stack(self, stack_name):
        stack = getattr(self, f"_{stack_name}", None)

        if stack is None:
            return []

        return self._values(stack)
    
    def __contains__(self, value):

        for name in _STACK_NAMES:

            stack = getattr(self, f"_{name}")

            if any(item["value"] == value for item in stack):
                return True

        return False
    
    def __iter__(self):

        for name in _STACK_NAMES:

            stack = getattr(self, f"_{name}")

            for item in stack:
                yield item

    def get_last_timestamp(self, stack_name):

        stack = getattr(self, f"_{stack_name}", None)

        if not stack:
            return None

        return stack[-1]["timestamp"]

    def touch(self, stack_name, value):

        stack = getattr(self, f"_{stack_name}", None)

        if stack is None:
            return

        self._push(stack, value)

    def all_values(self):

        return {

            name: self._values(getattr(self, f"_{name}"))

            for name in _STACK_NAMES

        }
    def _push(self, stack: deque, value):
        """
        Inserta un valor en la pila, eliminando duplicados previos.
        Cada elemento se guarda con su timestamp.
        """
        if value is None:
            return None

        # Eliminar duplicados previos
        for item in list(stack):
            if item["value"] == value:
                stack.remove(item)

        stack.append({"value": value, "timestamp": datetime.now().isoformat()})
        return value


    def last(self):
        """
        Devuelve el último elemento global de todas las pilas.
        Incluye el tipo de pila, el valor y el timestamp.
        """
        for name in _STACK_NAMES:
            stack = getattr(self, f"_{name}")
            if stack:
                return {
                    "type": name,
                    "value": stack[-1]["value"],
                    "timestamp": stack[-1]["timestamp"]
                }
        return None
