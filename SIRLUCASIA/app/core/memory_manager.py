from app.utils.json_manager import JSONManager
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
import json
from datetime import datetime

# ==================================================
# MemoryManager v3
# Sistema de memoria inteligente para SIRLUCAS AI
# ==================================================

class MemoryManager:

    def __init__(self):
        self.memory = JSONManager.load("data/memory.json")
        if self.memory is None:
            self.memory = {}

    # ==================================================
    # Dispatcher
    # ==================================================
    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)

        if method is None:
            return ActionResult(False, ActionStatus.ERROR, "memory", command, f"No existe el comando '{command}'.")
        return method(data)

    # ==================================================
    # Guardar información
    # ==================================================
    def remember(self, data):
        key = data.get("key")
        value = data.get("value")
        category = data.get("category", "general")
        importance = data.get("importance", 2)
        now = datetime.now().isoformat()

        if not key or value is None:
            return ActionResult(False, ActionStatus.ERROR, "memory", "remember", "Clave o valor inválido.")

        self.memory[key] = {
            "value": value,
            "category": category,
            "created_at": now,
            "updated_at": now,
            "importance": importance,
            "source": "user",
            "times_used": 0,
            "last_access": None,
            "aliases": [],
            "tags": []
        }
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "remember", f"Recordaré que tu {key} es {value}.", self.memory[key])

    # ==================================================
    # Actualizar información
    # ==================================================
    def update(self, data):
        key = data.get("key")
        value = data.get("value")
        now = datetime.now().isoformat()

        if not key or value is None:
            return ActionResult(False, ActionStatus.ERROR, "memory", "update", "Clave o valor inválido.")

        if key not in self.memory:
            return ActionResult(False, ActionStatus.WARNING, "memory", "update", f"No existe '{key}' en memoria.")

        self.memory[key]["value"] = value
        self.memory[key]["updated_at"] = now
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "update", f"He actualizado tu {key} a {value}.", self.memory[key])

    # ==================================================
    # Recuperar información
    # ==================================================
    def recall(self, data):
        key = data.get("key")
        if not key:
            return ActionResult(False, ActionStatus.ERROR, "memory", "recall", "No especificaste qué recordar.")

        value = self.memory.get(key)
        if value is None:
            return ActionResult(False, ActionStatus.WARNING, "memory", "recall", f"No recuerdo tu {key}.")

        # Actualizar estadísticas
        self.increment_usage(key)
        self.touch(key)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "recall", value["value"], value)

    # ==================================================
    # Métodos internos
    # ==================================================
    def get(self, key):
        return self.memory.get(key)

    def set(self, key, value, category="general", importance=2):
        now = datetime.now().isoformat()
        self.memory[key] = {
            "value": value,
            "category": category,
            "created_at": now,
            "updated_at": now,
            "importance": importance,
            "source": "system",
            "times_used": 0,
            "last_access": None,
            "aliases": [],
            "tags": []
        }
        JSONManager.save("data/memory.json", self.memory)

    def increment_usage(self, key):
        if key in self.memory:
            self.memory[key]["times_used"] += 1
            JSONManager.save("data/memory.json", self.memory)

    def touch(self, key):
        if key in self.memory:
            self.memory[key]["last_access"] = datetime.now().isoformat()
            JSONManager.save("data/memory.json", self.memory)

    # ==================================================
    # Búsquedas avanzadas
    # ==================================================
    def find_by_category(self, category):
        return {k: v for k, v in self.memory.items() if v.get("category") == category}

    def find_by_tag(self, tag):
        return {k: v for k, v in self.memory.items() if tag in v.get("tags", [])}

    def find_by_alias(self, alias):
        return {k: v for k, v in self.memory.items() if alias in v.get("aliases", [])}

    def search(self, data=None):
        query = data.get("query", "").lower() if data else ""
        results = {k: v for k, v in self.memory.items() if query in v["value"].lower()}
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "search", f"Resultados para '{query}'", results)

    # ==================================================
    # Estadísticas
    # ==================================================
    def statistics(self):
        total = len(self.memory)
        categorias = {}
        mas_usadas = sorted(self.memory.items(), key=lambda x: x[1]["times_used"], reverse=True)[:5]
        ultimo_acceso = max(self.memory.items(), key=lambda x: x[1]["last_access"] or "", default=None)

        for k, v in self.memory.items():
            cat = v.get("category", "general")
            categorias[cat] = categorias.get(cat, 0) + 1

        stats = {
            "total": total,
            "categorias": categorias,
            "mas_usadas": mas_usadas,
            "ultimo_acceso": ultimo_acceso
        }
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "statistics", "Estadísticas de memoria.", stats)

    # ==================================================
    # Exportar / Importar / Backup
    # ==================================================
    def export(self, data=None):
        JSONManager.save("data/memory.json", self.memory)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "export", "Memoria exportada correctamente.")

    def import_memories(self, data=None):
        archivo = data.get("file", "data/memory.json")
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = json.load(f)
            self.memory.update(contenido)
            JSONManager.save("data/memory.json", self.memory)
            return ActionResult(True, ActionStatus.SUCCESS, "memory", "import", "Memoria importada correctamente.", self.memory)
        except Exception as e:
            return ActionResult(False, ActionStatus.ERROR, "memory", "import", f"Error al importar: {str(e)}")

    def backup(self):
        JSONManager.save("data/memory_backup.json", self.memory)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "backup", "Backup creado en memory_backup.json.")

    def restore(self):
        contenido = JSONManager.load("data/memory_backup.json")
        if contenido:
            self.memory = contenido
            JSONManager.save("data/memory.json", self.memory)
            return ActionResult(True, ActionStatus.SUCCESS, "memory", "restore", "Memoria restaurada desde backup.")
        return ActionResult(False, ActionStatus.ERROR, "memory", "restore", "No se encontró backup.")

    def sync(self):
        JSONManager.save("data/memory.json", self.memory)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "sync", "Memoria sincronizada.")

    def validate(self):
        try:
            with open("data/memory.json", "r", encoding="utf-8") as f:
                json.load(f)
            return ActionResult(True, ActionStatus.SUCCESS, "memory", "validate", "Archivo memory.json válido.")
        except Exception as e:

            return ActionResult(False, ActionStatus.ERROR, "memory", "validate", f"Archivo corrupto: {str(e)}")
    # ==================================================
    # Eliminar memoria
    # ==================================================
    def forget(self, data):
        key = data.get("key")

        if not key:
            return ActionResult(
                False,
                ActionStatus.ERROR,
                "memory",
                "forget",
                "No especificaste la memoria a eliminar."
            )

        if key not in self.memory:
            return ActionResult(
                False,
                ActionStatus.WARNING,
                "memory",
                "forget",
                f"No existe '{key}' en memoria."
            )

        del self.memory[key]
        JSONManager.save("data/memory.json", self.memory)

        return ActionResult(
            True,
            ActionStatus.SUCCESS,
            "memory",
            "forget",
            f"He olvidado '{key}'."
        )
    def remove(self, data):
        return self.forget(data)

    # ==================================================
    # Verificar existencia
    # ==================================================
    def exists(self, key):
        return key in self.memory

    # ==================================================
    # Contar memorias
    # ==================================================
    def count(self, data=None):

        return ActionResult(
            True,
            ActionStatus.SUCCESS,
            "memory",
            "count",
            f"Tengo {len(self.memory)} memorias.",
            {
                "count": len(self.memory)
            }
        )
    # ==================================================
    # Listar memorias
    # ==================================================
    def list_memories(self, data=None):

        if not self.memory:
            return ActionResult(
                False,
                ActionStatus.WARNING,
                "memory",
                "list_memories",
                "No hay memorias almacenadas."
            )

        return ActionResult(
            True,
            ActionStatus.SUCCESS,
            "memory",
            "list_memories",
            "Listado de memorias.",
            self.memory
        )
    # ==================================================
    # Obtener contexto para IA
    # ==================================================
    def get_context(self):

        return {
            key: value["value"]
            for key, value in self.memory.items()
        }
    # ==================================================
    # Obtener memorias relevantes
    # ==================================================
    def get_relevant(self, text):

        text = text.lower()

        results = {}

        for key, value in self.memory.items():

            if key.lower() in text:

                results[key] = value

        return results
    # ==================================================
    # Resumen de memoria
    # ==================================================
    def summarize(self):

        if not self.memory:
            return "No tengo recuerdos."

        resumen = []

        for key, value in self.memory.items():
            resumen.append(f"{key}: {value['value']}")

        return "\n".join(resumen)