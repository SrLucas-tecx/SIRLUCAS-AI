from datetime import datetime
import json
import uuid
from app.database.history_database import HistoryDatabase
from app.utils.json_manager import JSONManager
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# HistoryManager
# Administrador completo del historial de SIRLUCAS AI
# ==================================================

class HistoryManager:

    def __init__(self):
        self.database = HistoryDatabase()

    # ===============================
    # Dispatcher
    # ===============================
    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return ActionResult(False, ActionStatus.ERROR, "history", command, f"No existe el comando '{command}'.")
        return method(data)

    # ===============================
    # Helpers internos
    # ===============================
    def get(self, record_id):
        for item in self.database.data:
            if item["id"] == record_id:
                return item
        return None

    def exists(self, record_id):
        return self.get(record_id) is not None

    def find(self, key, value):
        return [item for item in self.database.data if str(item.get(key, "")).lower() == str(value).lower()]

    def find_module(self, module):
        return self.find("module", module)

    def find_command(self, command):
        return self.find("command", command)

    # ===============================
    # Registrar comando
    # ===============================
    def add(self, module, command, topic=None, status=None, result=None, duration=None, user_input=None):
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "module": module,
            "command": command,
            "topic": topic,
            "status": status,
            "result": result,
            "duration": duration,
            "user_input": user_input
        }
        self.database.data.append(record)
        self.sync()
        return ActionResult(True, ActionStatus.SUCCESS, "history", "add", "Registro agregado.", record)

    # ===============================
    # Obtener historial
    # ===============================
    def history(self, data=None):
        limit = data.get("limit") if data else None
        reverse = data.get("reverse", False) if data else False

        records = self.database.data[::-1] if reverse else self.database.data
        if limit:
            records = records[-limit:]

        return ActionResult(True, ActionStatus.SUCCESS, "history", "history", "Historial obtenido.", records)

    # ===============================
    # Último comando
    # ===============================
    def last(self, data=None):
        if not self.database.data:
            return ActionResult(False, ActionStatus.WARNING, "history", "last", "Historial vacío.")
        return ActionResult(True, ActionStatus.SUCCESS, "history", "last", "Último registro.", self.database.data[-1])

    # ===============================
    # Limpiar historial
    # ===============================
    def clear(self, data=None):
        self.database.data.clear()
        self.sync()
        return ActionResult(True, ActionStatus.SUCCESS, "history", "clear", "Historial limpiado.")

    # ===============================
    # Buscar en historial
    # ===============================
    def search(self, data):
        query = str(data.get("query", "")).lower()
        results = [
            item for item in self.database.data
            if query in str(item.get("command", "")).lower()
            or query in str(item.get("module", "")).lower()
            or query in str(item.get("topic", "")).lower()
        ]
        return ActionResult(True, ActionStatus.SUCCESS, "history", "search", f"{len(results)} resultados encontrados.", results)

    def history_by_module(self, data):
        module = data.get("module")
        if not module:
            return ActionResult(False, ActionStatus.ERROR, "history", "history_by_module", "Módulo no especificado.")
        results = self.find_module(module)
        return ActionResult(True, ActionStatus.SUCCESS, "history", "history_by_module", f"{len(results)} registros para módulo {module}.", results)

    def history_by_date(self, data):
        date = data.get("date")
        if not date:
            return ActionResult(False, ActionStatus.ERROR, "history", "history_by_date", "Fecha no especificada.")
        results = [item for item in self.database.data if item.get("timestamp", "").startswith(date)]
        return ActionResult(True, ActionStatus.SUCCESS, "history", "history_by_date", f"{len(results)} registros para fecha {date}.", results)

    def last_n(self, data):
        n = data.get("n", 5)
        results = self.database.data[-n:]
        return ActionResult(True, ActionStatus.SUCCESS, "history", "last_n", f"Últimos {n} registros.", results)

    def count(self, data=None):
        total = len(self.database.data)
        return ActionResult(True, ActionStatus.SUCCESS, "history", "count", f"Total: {total}", {"count": total})

    # ===============================
    # Estadísticas
    # ===============================
    def statistics(self, data=None):
        total = len(self.database.data)
        if not total:
            return ActionResult(False, ActionStatus.WARNING, "history", "statistics", "Historial vacío.")

        modules = [item["module"] for item in self.database.data if item.get("module")]
        commands = [item["command"] for item in self.database.data if item.get("command")]

        stats = {
            "total": total,
            "modules": list(set(modules)),
            "modules_count": {m: modules.count(m) for m in set(modules)},
            "commands": list(set(commands)),
            "commands_count": {c: commands.count(c) for c in set(commands)},
            "most_used_command": max(set(commands), key=commands.count) if commands else None,
            "most_used_module": max(set(modules), key=modules.count) if modules else None,
            "first_record": self.database.data[0],
            "last_record": self.database.data[-1],
            "start_date": self.database.data[0]["timestamp"],
            "end_date": self.database.data[-1]["timestamp"]
        }
        return ActionResult(True, ActionStatus.SUCCESS, "history", "statistics", "Estadísticas generadas.", stats)

    # ===============================
    # Resumen
    # ===============================
    def summary(self, data=None):
        if not self.database.data:
            return ActionResult(False, ActionStatus.WARNING, "history", "summary", "Historial vacío.")

        total = len(self.database.data)
        modules = list(set([item["module"] for item in self.database.data if item.get("module")]))
        commands = [item["command"] for item in self.database.data if item.get("command")]
        most_used_command = max(set(commands), key=commands.count) if commands else None
        last_command = self.database.data[-1]

        resumen = (
            f"Total de registros: {total}\n"
            f"Módulos utilizados: {', '.join(modules)}\n"
            f"Comando más frecuente: {most_used_command}\n"
            f"Último comando: {last_command['command']} ({last_command['module']})\n"
            f"Fecha inicial: {self.database.data[0]['timestamp']}\n"
            f"Fecha final: {self.database.data[-1]['timestamp']}"
        )

        return ActionResult(True, ActionStatus.SUCCESS, "history", "summary", "Resumen generado.", resumen)

    # ===============================
    # Eliminar registros
    # ===============================
    def remove(self, data):
        idx = data.get("id")
        if not idx:
            return ActionResult(False, ActionStatus.ERROR, "history", "remove", "ID no especificado.")
        item = self.get(idx)
        if not item:
            return ActionResult(False, ActionStatus.WARNING, "history", "remove", f"No se encontró registro {idx}.")
        self.database.data.remove(item)
        self.sync()
        return ActionResult(True, ActionStatus.SUCCESS, "history", "remove", f"Registro {idx} eliminado.")

    def remove_last(self, data=None):
        if not self.database.data:
            return ActionResult(False, ActionStatus.WARNING, "history", "remove_last", "Historial vacío.")
        item = self.database.data.pop()
        self.sync()
        return ActionResult(True, ActionStatus.SUCCESS, "history", "remove_last", "Último registro eliminado.", item)

    # ===============================
    # Exportar / Importar / Backup
    # ===============================
    def export(self, data=None):
        JSONManager.save("data/history.json", self.database.data)
        return ActionResult(True, ActionStatus.SUCCESS, "history", "export", "Historial exportado.")

    def import_history(self, data):
        archivo = data.get("file", "data/history.json")
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido = json.load(f)
            self.database.data = contenido
            self.sync()
            return ActionResult(True, ActionStatus.SUCCESS, "history", "import_history", "Historial importado.", contenido)
        except Exception as e:
            return ActionResult(False, ActionStatus.ERROR, "history", "import_history", f"Error al importar: {str(e)}")

    def backup(self, data=None):
        JSONManager.save("data/history_backup.json", self.database.data)
        return ActionResult(True, ActionStatus.SUCCESS, "history", "backup", "Backup creado.")    

    def restore(self, data=None):
        contenido = JSONManager.load("data/history_backup.json")
        if contenido:
            self.database.data = contenido
            self.sync()
            return ActionResult(True, ActionStatus.SUCCESS, "history", "restore", "Historial restaurado.")
        return ActionResult(False, ActionStatus.ERROR, "history", "restore", "No se encontró backup.")

    def sync(self, data=None):
        JSONManager.save("data/history.json", self.database.data)
        return ActionResult(True, ActionStatus.SUCCESS, "history", "sync", "Historial sincronizado.")

    def validate(self, data=None):
        try:
            with open("data/history.json", "r", encoding="utf-8") as f:
                json.load(f)
            return ActionResult(True, ActionStatus.SUCCESS, "history", "validate", "Archivo válido.")
        except Exception as e:
            return ActionResult(False, ActionStatus.ERROR, "history", "validate", f"Archivo corrupto: {str(e)}")

    # ===============================
    # Representación
    # ===============================
    def __repr__(self):
        return f"<HistoryManager total={len(self.database.data)} modules={len(set([i['module'] for i in self.database.data if i.get('module')]))}>"
