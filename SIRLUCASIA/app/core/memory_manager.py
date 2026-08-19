"""
MemoryManager
==============
Sistema de memoria a largo plazo de SIRLUCAS AI.

Este módulo mantiene compatibilidad TOTAL con la API pública anterior:
`execute()`, `remember()`, `update()`, `recall()`, `forget()`, `search()`,
`statistics()`, `summary()` (nuevo), `count()`, `export()`, `backup()`,
`restore()`, `sync()`, `validate()` siguen funcionando exactamente igual
para quien ya las use, además de sumar CRUD extendido, búsquedas,
estadísticas, "inteligencia" básica y utilidades de nivel profesional.

Organización del archivo
-------------------------
    1. Constantes
    2. Inicialización
    3. Dispatcher
    4. CRUD de memoria
    5. Búsquedas
    6. Estadísticas
    7. Inteligencia
    8. Persistencia
    9. Utilidades / helpers privados
    10. Serialización
    11. Representación (dunder methods)

Optimización de escritura (dirty flag)
----------------------------------------
Las operaciones estructurales (remember/update/forget/rename/...) siguen
persistiendo en disco de inmediato por defecto (autosave_enabled=True),
igual que en la versión anterior, para no cambiar el comportamiento
observable. Si se instancia con `autosave_enabled=False`, esas mismas
operaciones dejan de forzar la escritura inmediata: solo marcan la
memoria como "dirty" (`mark_dirty()`) y el volcado real ocurre en
`save()`, `sync()`, `export()` o `autosave()`. El bookkeeping de lectura
(`recall()`: contador de uso, último acceso) NUNCA golpea el disco de
inmediato, sin importar `autosave_enabled`: solo marca "dirty".

Índices internos (categoría / etiquetas)
------------------------------------------
`find_by_category`, `find_by_tag`, `categories()`, `tags()` y
`statistics()` ya no recorren linealmente todo `self.memory` en cada
llamada. Se mantienen dos índices invertidos en memoria,
`self._category_index` y `self._tag_index` (dict[str, set[str]]), que se
actualizan de forma incremental en cada punto de mutación (remember,
update, forget, rename, duplicate, merge, clear, clear_category, restore,
import_memories, from_dict, set). Las etiquetas (y los aliases) se
normalizan a minúsculas al crear el registro, así `find_by_tag("Project")`
y `find_by_tag("project")` encuentran lo mismo.

Concurrencia
-------------
Se agregó un `threading.RLock` (`self._lock`) que protege las secciones
de lectura-modificación-escritura de las operaciones estructurales y de
`save()`. Esto no cambia ninguna firma ni ningún valor de retorno: solo
hace que la clase sea segura de usar desde varios hilos (por ejemplo, si
en el futuro el Router despacha comandos de memoria de forma concurrente).

Escalabilidad
--------------
Toda la persistencia pasa por dos métodos privados, `_read_storage()` y
`_write_storage()`, que hoy delegan en `JSONManager`. Migrar a SQLite,
PostgreSQL o MongoDB en el futuro implica reemplazar únicamente esos dos
métodos: la API pública (`remember`, `recall`, `search`, etc.) no cambia.

TODO (mejoras que SÍ tocarían la arquitectura y por eso NO se implementan
aquí, solo se dejan preparadas):
    - Índice de aliases (`self._alias_index`): hoy `find_by_alias` y
      `resolve_alias` siguen siendo O(n). Se podría indexar igual que
      categoría/tags, pero como los aliases pueden repetirse o
      colisionar entre memorias, requeriría definir una política de
      resolución (primer match, error, lista) que hoy no está
      especificada por el comportamiento original. Se deja documentado
      para no alterar el comportamiento observable actual.
    - `score_relevance` / `rank_memories` podrían apoyarse en embeddings
      reales (ver `search_semantic`, que ya actúa como "seam" para eso)
      en vez de la heurística de substring + importancia + uso. El
      cálculo de score es la única pieza a reemplazar; la firma pública
      no cambiaría. IMPORTANTE: `search_semantic()` hoy es un alias de
      `search_text()` (substring matching). NO hay embeddings ni base de
      datos vectorial todavía; se deja como interfaz preparada para
      integrarse con Ollama en el futuro.
    - `_read_storage` / `_write_storage` migrando a SQLite/Postgres/Mongo
      permitirían mover los índices de categoría/tags a consultas nativas
      (WHERE category = ?), eliminando la necesidad de mantenerlos a mano
      en Python. Mientras la persistencia sea un único JSON, mantener los
      índices en memoria es la mejora correcta.

Nota de mantenimiento (fix aplicado)
--------------------------------------
`_persist()` marcaba la memoria como "dirty" pero NUNCA revisaba
`self.autosave_enabled`, así que con autosave_enabled=True (el valor por
defecto) las operaciones estructurales dejaban de escribir a disco de
inmediato, contradiciendo lo documentado arriba y rompiendo la
compatibilidad hacia atrás. Se corrigió para que `_persist()` llame a
`save()` cuando `autosave_enabled` es True. También se corrigió
`restore()` para distinguir "no existe backup" (`None`) de "backup vacío"
(`{}`), que antes se trataban igual.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime
from typing import Any

from app.utils.json_manager import JSONManager
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# 1. CONSTANTES
# ==================================================
import os

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MEMORY_PATH = os.path.join(_BASE_DIR, "data", "memory.json")
BACKUP_PATH = os.path.join(_BASE_DIR, "data", "memory_backup.json")

DEFAULT_CATEGORY = "general"
MIN_IMPORTANCE = 1
MAX_IMPORTANCE = 5
DEFAULT_IMPORTANCE = 2
DEFAULT_FIND_LIMIT = 5
DEFAULT_RELEVANT_MEMORY_LIMIT = 5

# Máximo de memorias de categoría 'conversation' (turnos) que se
# conservan. Evita que memory.json crezca sin límite y que
# get_relevant_memory() se llene de ruido con cada turno de charla.
MAX_CONVERSATION_TURNS = 50


class MemoryRecord(dict):
    """Compatibilidad legacy: un registro estructurado sigue siendo dict
    para la app, pero se compara igual a su valor simple cuando el código
    heredado espera `memory.memory['nombre'] == 'Juan'`.
    """

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self.get("value")) == other
        return super().__eq__(other)

    def __str__(self):
        return str(self.get("value"))


class MemoryManager:
    """Administrador de memoria a largo plazo de SIRLUCAS AI."""

    # Comandos permitidos a través de execute()/dispatcher. Restringe la
    # superficie invocable por nombre de comando a los métodos que siguen
    # el contrato `method(data: dict) -> ActionResult`. Métodos como
    # get/exists/set/resolve_alias usan otra firma (argumentos
    # posicionales) y se llaman directamente en Python, no vía execute().
    COMMANDS = {
        "remember",
        "update",
        "forget",
        "remove",
        "recall",
        "search",
        "search_text",
        "search_semantic",
        "find_by_category",
        "list_by_category",
        "search_by_category",
        "find_by_tag",
        "find_by_alias",
        "find_by_importance",
        "find_recent",
        "find_old",
        "find_unused",
        "statistics",
        "summary",
        "count",
        "most_used",
        "least_used",
        "categories",
        "tags",
        "memory_size",
        "get_context",
        "rank_memories",
        "suggest_memories",
        "consult",
        "remember_turn",
        "find_similar",
        "get_relevant_memory",
        "autosave",
        "save",
        "backup",
        "restore",
        "sync",
        "validate",
        "export",
        "import_memories",
        "clear",
        "clear_category",
        "rename",
        "duplicate",
        "merge",
        "remember_fact",
        "remember_project",
        "get_project",
        "set_autosave",
        "autosave_status",
    }

    # ==================================================
    # 2. INICIALIZACIÓN
    # ==================================================
    def __init__(self, autosave_enabled: bool = True) -> None:
        """
        Inicializa el administrador de memoria.

        autosave_enabled:
            True  -> las operaciones estructurales se guardan inmediatamente.
            False -> las operaciones estructurales solo marcan la memoria
                     como dirty y el guardado se realiza mediante save(),
                     sync(), autosave() o export().
        """
        # Lock de reentrancia: protege las operaciones estructurales y el
        # volcado a disco frente a acceso concurrente desde varios hilos.
        self._lock = threading.RLock()

        self.autosave_enabled = bool(autosave_enabled)

        raw_memory = self._read_storage(MEMORY_PATH)

        self.memory: dict[str, MemoryRecord] = {}
        if isinstance(raw_memory, dict):
            for key, record in raw_memory.items():
                normalized = self._normalize_record(record)
                self.memory[self._normalize(key)] = MemoryRecord(normalized)

        self._dirty: bool = False
        self._last_saved_at: str | None = None

        # Índices invertidos categoría -> {claves} y etiqueta -> {claves},
        # reconstruidos a partir de lo cargado desde disco.
        self._category_index: dict[str, set[str]] = {}
        self._tag_index: dict[str, set[str]] = {}
        self._index_rebuild()

    # ==================================================
    # 3. DISPATCHER
    # ==================================================
    def execute(self, data: dict) -> ActionResult:
        """
        Punto de entrada uniforme usado por el resto de SIRLUCAS AI
        (Router/TaskExecutor). Nunca lanza excepciones: cualquier fallo
        se envuelve en un ActionResult de error. Solo permite ejecutar
        comandos explícitamente registrados en `COMMANDS`.
        """
        command = data.get("command") if isinstance(data, dict) else None

        if not command:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command=command,
                message="No se especificó un comando."
            )

        if command not in self.COMMANDS:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command=command,
                message=f"No existe el comando '{command}'."
            )

        method = getattr(self, command, None)
        if not callable(method):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command=command,
                message=f"El comando '{command}' no es ejecutable."
            )

        try:
            result = method(data)
        except Exception as exc:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command=command,
                message=f"Error ejecutando '{command}': {exc}"
            )

        if isinstance(result, ActionResult):
            return result

        # Compatibilidad: si un método devuelve un valor "crudo", se
        # envuelve automáticamente para mantener un contrato uniforme.
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command=command,
            message="OK",
            data=result
        )

    # ==================================================
    # 4. CRUD DE MEMORIA
    # ==================================================
    def remember(self, data: dict) -> ActionResult:
        """Crea o sobreescribe una memoria. (Firma y mensajes sin cambios)."""
        if not isinstance(data, dict):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember",
                message="Clave o valor inválido."
            )

        key = self._normalize(data.get("key"))
        value = data.get("value")
        category = self._normalize_category(data.get("category"))
        importance = self._clamp_importance(data.get("importance", DEFAULT_IMPORTANCE))

        if not key.strip():
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember",
                message="clave inválida."
            )

        if value is None or (isinstance(value, str) and not value.strip()):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember",
                message="valor inválido."
            )

        record = MemoryRecord(self._create_record(
            value,
            category=category,
            importance=importance,
            source=data.get("source", "user"),
            aliases=data.get("aliases"),
            tags=data.get("tags"),
        ))

        with self._lock:
            existing = self.memory.get(key)
            if existing is not None:
                # Preserva id y fecha de creación originales si la clave ya existía.
                record["id"] = existing.get("id", record["id"])
                record["created_at"] = existing.get("created_at", record["created_at"])
                self._index_remove(key, existing)

            self.memory[key] = record
            self._index_add(key, record)
            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="remember",
            message=f"Recordaré que tu {key} es {value}.",
            data=record
        )

    def __getitem__(self, key: str):
        """Compatibilidad legacy: memory['key'] devuelve el valor almacenado."""
        record = self.memory.get(self._normalize(key))
        if record is None:
            raise KeyError(key)
        return record.get("value")

    def __setitem__(self, key: str, value: Any):
        """Compatibilidad legacy: memory['key'] = value guarda el valor sin tipo record."""
        self.remember({"key": key, "value": value})

    def update(self, data: dict) -> ActionResult:
        """Actualiza el valor (y opcionalmente categoría/importancia) de una memoria existente."""
        key = self._normalize(data.get("key"))
        value = data.get("value")

        if not self._validate_key_value(key, value):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="update",
                message="Clave o valor inválido."
            )

        with self._lock:
            if key not in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="update",
                    message=f"No existe '{key}' en memoria."
                )

            record = self.memory[key]
            # Se retira del índice con el estado "viejo" y se vuelve a
            # indexar al final, así categoría/tags quedan siempre
            # consistentes sin importar qué campo haya cambiado.
            self._index_remove(key, record)

            record["value"] = value
            record["updated_at"] = self._now()

            if data.get("category"):
                record["category"] = self._normalize_category(data["category"])
            if data.get("importance") is not None:
                record["importance"] = self._clamp_importance(data["importance"])

            self._index_add(key, record)
            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="update",
            message=f"He actualizado tu {key} a {value}.",
            data=record
        )

    def forget(self, data: dict) -> ActionResult:
        """Elimina una memoria por clave."""
        if not isinstance(data, dict):
            data = {}
        key = self._normalize(data.get("key"))

        valid_key, _ = self._validate_key(key)
        if not valid_key:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="forget",
                message="No especificaste qué olvidar."
            )

        with self._lock:
            if key not in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="forget",
                    message=f"No existe '{key}' en memoria."
                )

            record = self.memory.pop(key)
            self._index_remove(key, record)
            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="forget",
            message=f"He olvidado '{key}'."
            )

    def remove(self, data: dict) -> ActionResult:
        """Alias histórico de `forget()`."""
        return self.forget(data)

    def exists(self, key: str | dict) -> bool:
        """Indica si una clave existe en memoria (firma original preservada)."""
        if isinstance(key, dict):
            key = key.get("key")
        return self._normalize(key) in self.memory

    def get(self, key: str) -> dict | None:
        """Devuelve el registro completo de una clave, o None (firma original preservada)."""
        return self.memory.get(self._normalize(key))

    def keys(self):
        """Compatibilidad con el API legacy: devuelve las claves de memoria."""
        return list(self.memory.keys())

    def values(self):
        """Compatibilidad con el API legacy: devuelve los valores de memoria."""
        return [record.get("value") if isinstance(record, dict) else record for record in self.memory.values()]

    def list_memories(self, data: dict | None = None) -> ActionResult:
        """Compatibilidad legacy: devuelve un resumen simple clave->valor."""
        serialized = {
            key: record.get("value") if isinstance(record, dict) else record
            for key, record in self.memory.items()
        }

        if not serialized:
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="list_memories",
                message="La memoria está vacía.",
                data={}
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="list_memories",
            message="Memorias actuales.",
            data=serialized
        )

    def set(self, key: str, value: Any, category: str = "general", importance: int = 2) -> dict:
        """Crea/sobreescribe una memoria "en frío", sin pasar por remember() (firma original preservada)."""
        key = self._normalize(key)
        record = self._create_record(
            value,
            category=self._normalize_category(category),
            importance=self._clamp_importance(importance),
            source="system",
        )
        with self._lock:
            existing = self.memory.get(key)
            if existing is not None:
                self._index_remove(key, existing)
            self.memory[key] = MemoryRecord(record)
            self._index_add(key, self.memory[key])
            self._persist()
        return self.memory[key]

    def clear(self, data: dict | None = None) -> ActionResult:
        """Elimina TODAS las memorias."""
        with self._lock:
            removed = len(self.memory)
            self.memory.clear()
            self._category_index.clear()
            self._tag_index.clear()
            self._persist()
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="clear",
            message="Memoria limpiada correctamente.",
            data={"removed": removed}
        )

    def clear_category(self, data: dict) -> ActionResult:
        """Elimina todas las memorias de una categoría."""
        category = self._normalize_category(data.get("category"))

        with self._lock:
            keys = list(self._category_index.get(category, ()))

            for key in keys:
                record = self.memory.pop(key, None)
                if record is not None:
                    self._index_remove(key, record)

            if keys:
                self._persist()

        status = ActionStatus.SUCCESS if keys else ActionStatus.WARNING
        message = (
            f"Se eliminaron {len(keys)} memorias de la categoría '{category}'."
            if keys
            else f"No había memorias en la categoría '{category}'."
        )
        return ActionResult(
            success=bool(keys),
            status=status,
            module="memory",
            command="clear_category",
            message=message,
            data={"removed": keys}
        )

    def rename(self, data: dict) -> ActionResult:
        """Renombra la clave de una memoria existente."""
        old_key = self._normalize(data.get("old_key") or data.get("key"))
        new_key = self._normalize(data.get("new_key"))

        valid_old, error_old = self._validate_key(old_key)
        if not valid_old:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="rename",
                message="No especificaste la memoria a renombrar."
            )

        valid_new, error_new = self._validate_key(new_key)
        if not valid_new:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="rename",
                message="No especificaste el nuevo nombre."
            )

        with self._lock:
            if old_key not in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="rename",
                    message=f"No existe '{old_key}' en memoria."
                )
            if new_key in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="memory",
                    command="rename",
                    message=f"Ya existe una memoria llamada '{new_key}'."
                )

            record = self.memory.pop(old_key)
            self._index_remove(old_key, record)

            record["updated_at"] = self._now()
            self.memory[new_key] = record
            self._index_add(new_key, record)

            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="rename",
            message=f"'{old_key}' ahora se llama '{new_key}'.",
            data=record
        )

    def duplicate(self, data: dict) -> ActionResult:
        """Crea una copia independiente de una memoria bajo una nueva clave."""
        source_key = self._normalize(data.get("key") or data.get("source_key"))
        target_key = self._normalize(data.get("new_key") or data.get("target_key"))

        with self._lock:
            if source_key not in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="duplicate",
                    message=f"No existe '{source_key}' en memoria."
                )

            valid_target, _ = self._validate_key(target_key)
            if not valid_target:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="memory",
                    command="duplicate",
                    message="No especificaste el nombre de la copia."
                )
            if target_key in self.memory:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="memory",
                    command="duplicate",
                    message=f"Ya existe una memoria llamada '{target_key}'."
                )

            record = json.loads(json.dumps(self.memory[source_key], default=str))
            record["id"] = self._generate_id()
            record["created_at"] = self._now()
            record["updated_at"] = record["created_at"]
            record["times_used"] = 0
            record["last_access"] = None

            self.memory[target_key] = record
            self._index_add(target_key, record)
            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="duplicate",
            message=f"'{source_key}' duplicado como '{target_key}'.",
            data=record
        )

    def merge(self, data: dict) -> ActionResult:
        """Combina varias memorias existentes en una sola nueva memoria."""
        keys = data.get("keys") or []
        target_key = self._normalize(data.get("new_key") or data.get("target_key"))

        valid_target, _ = self._validate_key(target_key)
        if not valid_target:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="merge",
                message="No especificaste el nombre de la memoria combinada."
            )

        with self._lock:
            existing = [self._normalize(k) for k in keys if self._normalize(k) in self.memory]
            if not existing:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="merge",
                    message="Ninguna de las memorias indicadas existe."
                )

            combined_value = "; ".join(str(self.memory[k]["value"]) for k in existing)
            category = data.get("category") or self.memory[existing[0]].get("category")
            importance = max(self.memory[k].get("importance", DEFAULT_IMPORTANCE) for k in existing)

            record = self._create_record(
                combined_value,
                category=self._normalize_category(category),
                importance=self._clamp_importance(importance),
                source="merge",
            )

            # Si target_key coincide con una clave ya existente (por ejemplo,
            # una de las fuentes), primero se retira su entrada vieja del
            # índice para no dejar referencias colgadas.
            if target_key in self.memory:
                self._index_remove(target_key, self.memory[target_key])

            self.memory[target_key] = record
            self._index_add(target_key, record)

            for key in existing:
                if key != target_key:
                    old = self.memory.pop(key, None)
                    if old is not None:
                        self._index_remove(key, old)

            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="merge",
            message=f"Se combinaron {len(existing)} memorias en '{target_key}'.",
            data=record
        )

    # ==================================================
    # 5. BÚSQUEDAS
    # ==================================================
    def recall(self, data: dict) -> ActionResult:
        """Recupera una memoria por clave (firma y mensajes originales preservados)."""
        key = self._normalize(data.get("key"))

        valid_key, _ = self._validate_key(key)
        if not valid_key:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="recall",
                message="No especificaste qué recordar."
            )

        with self._lock:
            record = self.memory.get(key)
            if record is None:
                return ActionResult(
                    success=False,
                    status=ActionStatus.WARNING,
                    module="memory",
                    command="recall",
                    message=f"No recuerdo tu {key}."
                )

            # Bookkeeping: NUNCA escribe a disco de inmediato, sin importar
            # autosave_enabled — solo marca la memoria como "dirty". El
            # volcado real ocurre en save()/sync()/export()/autosave().
            self._increment_usage(key)
            self._touch(key)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="recall",
            message=record["value"],
            data=record
        )

    def search(self, data: dict | None = None) -> ActionResult:
        """Búsqueda de texto libre sobre valores y claves (comportamiento original preservado y extendido)."""
        query = (data.get("query", "") if data else "").strip().lower()
        if not query:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="search",
                message="No especificaste qué buscar."
            )

        results = {
            key: record
            for key, record in self.memory.items()
            if query in str(record.get("value", "")).lower() or query in key.lower()
        }

        status = ActionStatus.SUCCESS if results else ActionStatus.WARNING
        message = f"Resultados para '{query}'." if results else f"No encontré resultados para '{query}'."
        return ActionResult(
            success=bool(results),
            status=status,
            module="memory",
            command="search",
            message=message,
            data=results
        )

    def search_text(self, data: dict | None = None) -> ActionResult:
        """Alias explícito de `search()` para búsquedas puramente textuales."""
        result = self.search(data)
        result.command = "search_text"
        return result

    def find_by_category(self, data: dict | str | None = None) -> dict | ActionResult:
        """
        O(k): usa el índice invertido de categorías en vez de escanear toda la memoria.
        
        Acepta dos formas:
        - Via execute(): data = {"category": "..."}
        - Via Python directo: category_str
        """
        if isinstance(data, dict):
            category = data.get("category", DEFAULT_CATEGORY)
            category = self._normalize_category(category)
            keys = self._category_index.get(category, ())
            results = {key: self.memory[key] for key in keys if key in self.memory}
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="find_by_category",
                message=f"Encontradas {len(results)} memorias en categoría '{category}'.",
                data=results
            )
        else:
            # Forma directa (compatibilidad)
            category = self._normalize_category(data)
            keys = self._category_index.get(category, ())
            return {key: self.memory[key] for key in keys if key in self.memory}

    def list_by_category(self, data: dict) -> ActionResult:
        """Alias compatible con las reglas de lenguaje natural."""
        result = self.find_by_category(data)
        result.command = "list_by_category"
        return result

    def search_by_category(self, data: dict) -> ActionResult:
        """Alias compatible con las reglas de lenguaje natural."""
        result = self.find_by_category(data)
        result.command = "search_by_category"
        return result

    def find_by_tag(self, data: dict | str | None = None) -> dict | ActionResult:
        """
        O(k): usa el índice invertido de etiquetas en vez de escanear toda la memoria.
        
        Acepta dos formas:
        - Via execute(): data = {"tag": "..."}
        - Via Python directo: tag_str
        """
        if isinstance(data, dict):
            tag = data.get("tag", "").strip()
            if not tag:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="memory",
                    command="find_by_tag",
                    message="No especificaste la etiqueta a buscar."
                )
            tag = self._normalize(tag).lower()
            keys = self._tag_index.get(tag, ())
            results = {key: self.memory[key] for key in keys if key in self.memory}
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="find_by_tag",
                message=f"Encontradas {len(results)} memorias con etiqueta '{tag}'.",
                data=results
            )
        else:
            # Forma directa (compatibilidad)
            tag = self._normalize(data or "").lower()
            keys = self._tag_index.get(tag, ())
            return {key: self.memory[key] for key in keys if key in self.memory}

    def find_by_alias(self, data: dict | str | None = None) -> dict | ActionResult:
        """
        Encuentra memorias por alias.
        
        Acepta dos formas:
        - Via execute(): data = {"alias": "..."}
        - Via Python directo: alias_str
        
        TODO: indexar aliases igual que categoría/tags si este método se
        vuelve un punto caliente. Se deja como escaneo lineal porque los
        aliases pueden repetirse entre memorias y el comportamiento
        original no define una política de desambiguación explícita.
        """
        if isinstance(data, dict):
            alias = data.get("alias", "").strip()
            if not alias:
                return ActionResult(
                    success=False,
                    status=ActionStatus.ERROR,
                    module="memory",
                    command="find_by_alias",
                    message="No especificaste el alias a buscar."
                )
            results = {k: v for k, v in self.memory.items() if alias in v.get("aliases", [])}
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="find_by_alias",
                message=f"Encontradas {len(results)} memorias con alias '{alias}'.",
                data=results
            )
        else:
            # Forma directa (compatibilidad)
            return {k: v for k, v in self.memory.items() if (data or "") in v.get("aliases", [])}

    def find_by_importance(self, data: dict | None = None) -> dict:
        """Encuentra memorias por nivel de importancia."""
        if isinstance(data, dict):
            importance = data.get("importance")
        else:
            importance = data if data is not None else DEFAULT_IMPORTANCE
        importance = self._clamp_importance(importance)
        return {k: v for k, v in self.memory.items() if v.get("importance") == importance}

    def find_recent(self, data: dict | None = None) -> dict:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("created_at") or "", reverse=True)
        return dict(items[:limit])

    def find_old(self, data: dict | None = None) -> dict:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("created_at") or "")
        return dict(items[:limit])

    def find_unused(self, data: dict | None = None) -> dict:
        return {k: v for k, v in self.memory.items() if not v.get("times_used")}

    # ==================================================
    # 6. ESTADÍSTICAS
    # ==================================================
    def statistics(self, data: dict | None = None) -> ActionResult:
        """Estadísticas generales de memoria (formato original preservado)."""
        categorias = self._category_counts()

        mas_usadas = sorted(self.memory.items(), key=lambda item: item[1].get("times_used", 0), reverse=True)[:5]
        ultimo_acceso = max(self.memory.items(), key=lambda item: item[1].get("last_access") or "", default=None)

        stats = {
            "total": len(self.memory),
            "categorias": categorias,
            "mas_usadas": mas_usadas,
            "ultimo_acceso": ultimo_acceso,
        }
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="statistics",
            message="Estadísticas de memoria.",
            data=stats
        )

    def summary(self, data: dict | None = None) -> ActionResult:
        """Resumen inteligente en lenguaje natural + estadísticas, listo para mostrarse o pasarse a un LLM."""
        stats_result = self.statistics()
        text = self.summarize()
        payload = {"resumen": text, "estadisticas": stats_result.data}
        message = text if self.memory else "No tengo recuerdos."
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="summary",
            message=message,
            data=payload
        )

    def count(self, data: dict | None = None) -> ActionResult:
        """Cantidad total de memorias almacenadas (firma y mensaje originales preservados)."""
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="count",
            message=f"Tengo {len(self.memory)} memorias.",
            data={"count": len(self.memory)}
        )

    def most_used(self, data: dict | None = None) -> ActionResult:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("times_used", 0), reverse=True)[:limit]
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="most_used",
            message="Memorias más usadas.",
            data=dict(items)
        )

    def least_used(self, data: dict | None = None) -> ActionResult:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("times_used", 0))[:limit]
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="least_used",
            message="Memorias menos usadas.",
            data=dict(items)
        )

    def categories(self, data: dict | None = None) -> ActionResult:
        """Categorías existentes con su cantidad de memorias."""
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="categories",
            message="Categorías disponibles.",
            data=self._category_counts()
        )

    def tags(self, data: dict | None = None) -> ActionResult:
        """Conjunto de todas las etiquetas usadas en memoria."""
        todas = sorted(tag for tag, keys in self._tag_index.items() if keys)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="tags",
            message="Etiquetas disponibles.",
            data=todas
        )

    def memory_size(self, data: dict | None = None) -> ActionResult:
        """Tamaño aproximado en bytes que ocupa la memoria serializada."""
        size_bytes = len(json.dumps(self.memory, ensure_ascii=False, default=str).encode("utf-8"))
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="memory_size",
            message=f"La memoria ocupa {size_bytes} bytes.",
            data={"bytes": size_bytes, "entries": len(self.memory)}
        )

    # ==================================================
    # 7. INTELIGENCIA
    # ==================================================
    def get_context(self, data: dict | None = None) -> dict:
        """Contexto plano clave->valor, pensado para pasarle a un LLM (firma original preservada)."""
        return {key: record["value"] for key, record in self.memory.items()}

    def get_relevant(self, text: str) -> dict:
        """Memorias cuya clave aparece mencionada en `text` (firma original preservada)."""
        if not text:
            return {}
        normalized_text = text.lower()
        return {key: record for key, record in self.memory.items() if key.lower() in normalized_text}

    def score_relevance(self, key: str, text: str) -> float:
        """
        Calcula qué tan relevante es una memoria para un texto.
        """

        normalized_key = self._normalize(key)
        record = self.memory.get(normalized_key)

        if record is None or not text:
            return 0.0

        normalized_text = str(text).lower()

        score = 0.0

        # --------------------------------------------------
        # CLAVE
        # --------------------------------------------------

        if normalized_key.lower() in normalized_text:
            score += 3.0

        # --------------------------------------------------
        # VALOR
        # --------------------------------------------------

        value = str(
            record.get("value", "")
        ).lower()

        if value and value in normalized_text:
            score += 4.0

        # --------------------------------------------------
        # ALIASES
        # --------------------------------------------------

        for alias in record.get("aliases", []):
            alias_text = str(alias).lower()

            if alias_text and alias_text in normalized_text:
                score += 3.0

        # --------------------------------------------------
        # TAGS
        # --------------------------------------------------

        for tag in record.get("tags", []):
            tag_text = str(tag).lower()

            if tag_text and tag_text in normalized_text:
                score += 1.5

        # --------------------------------------------------
        # CATEGORÍA
        # --------------------------------------------------

        category = str(
            record.get("category", "")
        ).lower()

        if category and category in normalized_text:
            score += 1.0

        # --------------------------------------------------
        # IMPORTANCIA
        # --------------------------------------------------

        score += (
            record.get(
                "importance",
                DEFAULT_IMPORTANCE
            ) * 0.2
        )

        # --------------------------------------------------
        # USO
        # --------------------------------------------------

        score += min(
            record.get("times_used", 0),
            10
        ) * 0.05

        return round(score, 3)

    def rank_memories(self, data: dict) -> ActionResult:
        """Ordena todas las memorias por relevancia respecto a un texto dado."""
        text = data.get("text", "") if isinstance(data, dict) else str(data or "")
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if isinstance(data, dict) else DEFAULT_FIND_LIMIT

        if not text:
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="rank_memories",
                message="Memorias ordenadas por relevancia.",
                data=[]
            )

        scored = (
            (key, self.score_relevance(key, text), record)
            for key, record in self.memory.items()
        )
        relevant = [item for item in scored if item[1] > 0]
        relevant.sort(key=lambda item: item[1], reverse=True)

        # Limitar resultados y devolver
        top = relevant[:limit]
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="rank_memories",
            message=f"Memorias ordenadas por relevancia respecto a '{text}'.",
            data=top
        )


    def suggest_memories(self, text: str = "", context: dict | None = None) -> ActionResult:
        """
        Sugiere las memorias más relevantes para un texto/contexto dado.
        Pensado como punto de integración de alto nivel (ver `consult`).
        """
        query_text = text or (context.get("last_user_message") if isinstance(context, dict) else "") or ""
        ranked = self.rank_memories({"text": query_text, "limit": DEFAULT_FIND_LIMIT})
        message = "Sugerencias de memoria." if ranked.data else "No encontré memorias relevantes."
        return ActionResult(
            success=bool(ranked.data),
            status=ranked.status,
            module=ranked.module,
            command=ranked.command,
            message=message,
            data=ranked.data
        )

    def consult(self, query: str, context: dict | None = None) -> ActionResult:
        """
        Punto de integración de alto nivel pensado para
        `ConversationManager._consult_memory()`: dado el mensaje del
        usuario y un snapshot de contexto opcional, sugiere memorias
        relevantes antes de ejecutar la acción.
        """
        return self.suggest_memories(query, context)

    def remember_turn(self, data: dict) -> ActionResult:
        """
        Punto de integración de alto nivel pensado para
        `ConversationManager._persist_memory()`: guarda un resumen del
        turno de conversación como memoria de categoría 'conversation'.

        Para evitar que memory.json crezca sin límite y que
        `get_relevant_memory()` se llene de ruido, solo se conservan como
        máximo `MAX_CONVERSATION_TURNS` memorias de esta categoría: al
        superar el límite se descarta primero el turno más antiguo.
        Si se necesita retener un dato de forma permanente (nombre de
        usuario, preferencias, proyecto actual, etc.) debe guardarse con
        `remember_fact()` / `remember_project()`, no con `remember_turn()`.
        """
        turn_id = data.get("turn_id") or self._generate_id()
        value = data.get("response") or data.get("message") or ""
        if not value:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="memory",
                command="remember_turn",
                message="El turno no tiene contenido para recordar."
            )

        result = self.remember({
            "key": f"turno:{turn_id}",
            "value": value,
            "category": "conversation",
            "importance": MIN_IMPORTANCE,
        })

        if result.success:
            self._trim_conversation_turns()

        return result

    def resolve_alias(self, alias: str) -> str | None:
        """Devuelve la clave "real" a la que apunta un alias, si existe."""
        normalized = self._normalize(alias).lower()
        for key, record in self.memory.items():
            if normalized in [str(a).lower() for a in record.get("aliases", [])]:
                return key
        return None

    def find_similar(self, data: dict) -> ActionResult:
        """
        Encuentra memorias "similares" a una dada por categoría y etiquetas
        compartidas. Heurística simple: la migración a similitud semántica
        real (embeddings) puede reemplazar el cálculo de `score` interno
        sin tocar la firma pública.
        """
        key = self._normalize(data.get("key")) if isinstance(data, dict) else self._normalize(data)
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if isinstance(data, dict) else DEFAULT_FIND_LIMIT

        record = self.memory.get(key)
        if record is None:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="memory",
                command="find_similar",
                message=f"No existe '{key}' en memoria."
            )

        category = record.get("category")
        tags = set(record.get("tags", []))

        # Se usan los índices para acotar de entrada el universo de
        # candidatos (misma categoría o alguna etiqueta compartida) en vez
        # de recorrer toda la memoria desde cero.
        candidate_keys = set(self._category_index.get(category, ()))
        for tag in tags:
            candidate_keys.update(self._tag_index.get(tag, ()))
        candidate_keys.discard(key)

        candidates = []
        for other_key in candidate_keys:
            other = self.memory.get(other_key)
            if other is None:
                continue
            overlap = len(tags.intersection(other.get("tags", [])))
            same_category = other.get("category") == category
            score = overlap * 2 + (1 if same_category else 0)
            if score > 0:
                candidates.append((other_key, score, other))

        candidates.sort(key=lambda item: item[1], reverse=True)
        similar = [{"key": k, "score": s, "record": r} for k, s, r in candidates[:limit]]

        message = "Memorias similares encontradas." if similar else "No se encontraron memorias similares."
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="find_similar",
            message=message,
            data=similar
        )

    def search_semantic(self, data: dict) -> ActionResult:
        """
        Seam para una futura búsqueda semántica basada en embeddings.
        Mientras no exista un backend vectorial, degrada de forma
        transparente a `search_text()` sin romper el contrato público.

        IMPORTANTE: esto todavía NO es búsqueda semántica real. No usa
        embeddings ni una base de datos vectorial: internamente llama a
        `search_text()`, que hace substring matching. Se deja como
        interfaz preparada para integrarse con Ollama en el futuro; no
        debe tratarse como semánticamente equivalente a una búsqueda por
        similitud real todavía.
        """
        result = self.search_text(data)
        result.command = "search_semantic"
        return result
        # ==================================================
        # 7. MEMORIA RELEVANTE PARA IA
        # ==================================================
    def get_relevant_memory(self, context: dict) -> list[str]:
        """
        Selecciona memorias permanentes relevantes para Ollama.
        """

        if not context:
            return []

        user_message = str(
            context.get("last_user_message") or ""
        ).lower()

        topic = str(
            context.get("topic") or ""
        ).lower()

        query = f"{user_message} {topic}".strip()

        if not query:
            return []

        # ------------------------------------------
        # Ranking normal
        # ------------------------------------------

        ranked = self.rank_memories({
            "text": query,
            "limit": 5
        })

        relevant = []

        for key, score, record in ranked.data or []:

            value = record.get("value")

            if value is None:
                continue

            # --------------------------------------
            # Proyecto
            # --------------------------------------

            if key.startswith("project:"):

                if isinstance(value, dict):
                    name = value.get("name", "")
                    description = value.get(
                        "description",
                        ""
                    )

                    relevant.append(
                        f"Proyecto: {name}. "
                        f"Descripción: {description}"
                    )

                else:
                    relevant.append(
                        f"Proyecto: {value}"
                    )

            # --------------------------------------
            # Memoria normal
            # --------------------------------------

            else:
                relevant.append(
                    f"{key}: {value}"
                )

        return relevant[:5]

    # ==================================================
    # 8. PERSISTENCIA
    # ==================================================
    def save(self, force: bool = False) -> bool:
        """
        Vuelca `self.memory` a disco SOLO si hay cambios pendientes
        (`self._dirty`) o si `force=True`. Devuelve True si escribió.
        """
        with self._lock:
            if not (self._dirty or force):
                return False

            self._write_storage(MEMORY_PATH, self.memory)
            self._dirty = False
            self._last_saved_at = self._now()
            return True

    def autosave(self, data: dict | None = None) -> ActionResult:
        """
        Guarda manualmente los cambios pendientes (usa el dirty flag).
        No depende de `autosave_enabled`: es una orden explícita de
        guardado, útil precisamente cuando el manager corre con
        `autosave_enabled=False`.
        """
        wrote = self.save(force=False)
        message = "Memoria sincronizada en disco." if wrote else "No había cambios pendientes."
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="autosave",
            message=message,
            data={
                "saved": wrote,
                "dirty": self._dirty,
                "last_saved_at": self._last_saved_at,
            }
        )

    def set_autosave(self, data: dict) -> ActionResult:
        """
        Activa o desactiva el guardado automático en caliente.

        Ejemplo:
            {"command": "set_autosave", "enabled": False}
        """
        if not isinstance(data, dict):
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="set_autosave",
                message="Datos inválidos."
            )

        if "enabled" not in data:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="set_autosave",
                message="No especificaste si autosave debe estar activo."
            )

        enabled = bool(data["enabled"])

        with self._lock:
            previous = self.autosave_enabled
            self.autosave_enabled = enabled

            # Si se acaba de activar y había cambios pendientes,
            # se guardan inmediatamente.
            if enabled and self._dirty:
                self.save(force=False)

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="set_autosave",
            message=(
                "Guardado automático activado."
                if enabled
                else "Guardado automático desactivado."
            ),
            data={
                "previous": previous,
                "enabled": self.autosave_enabled,
                "dirty": self._dirty,
                "last_saved_at": self._last_saved_at,
            }
        )

    def autosave_status(self, data: dict | None = None) -> ActionResult:
        """Devuelve el estado actual del sistema de persistencia."""
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="autosave_status",
            message="Estado de autosave obtenido.",
            data={
                "autosave_enabled": self.autosave_enabled,
                "dirty": self._dirty,
                "last_saved_at": self._last_saved_at,
                "entries": len(self.memory),
            }
        )

    def mark_dirty(self) -> None:
        """Marca la memoria como modificada, pendiente de persistir."""
        self._dirty = True

    def _persist(self) -> None:
        """
        Helper interno usado por todas las operaciones estructurales
        (remember/update/forget/rename/duplicate/merge/set/clear/...).

        Siempre marca la memoria como "dirty". Además, si
        `autosave_enabled` es True (valor por defecto), fuerza el volcado
        inmediato a disco llamando a `save()`, que es el comportamiento
        legado documentado en el módulo. Si `autosave_enabled` es False,
        solo queda marcada como dirty y el volcado real se difiere hasta
        `save()`, `sync()`, `export()` o `autosave()`.

        FIX: antes esta función solo llamaba a `mark_dirty()` sin revisar
        `autosave_enabled`, por lo que incluso con el valor por defecto
        (True) las operaciones estructurales dejaban de escribirse a
        disco de inmediato, contradiciendo el comportamiento documentado.
        """
        self.mark_dirty()
        if self.autosave_enabled:
            self.save()

    def export(self, data: dict | None = None) -> ActionResult:
        """Exporta la memoria completa a `data/memory.json` (o a `data.path` si se indica)."""
        path = (data.get("path") if data else None) or MEMORY_PATH
        with self._lock:
            self._write_storage(path, self.memory)
            self._dirty = False
            self._last_saved_at = self._now()
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="export",
            message="Memoria exportada correctamente.",
            data={"path": path}
            )

    def import_memories(self, data: dict | None = None) -> ActionResult:
        """Importa memorias desde un archivo JSON externo, fusionándolas con las actuales."""
        archivo = (data.get("file") if data else None) or MEMORY_PATH
        try:
            with open(archivo, "r", encoding="utf-8") as file_handle:
                contenido = json.load(file_handle)

            if not isinstance(contenido, dict):
                raise ValueError("El archivo no contiene un objeto JSON válido.")

            with self._lock:
                for key, record in contenido.items():
                    self.memory[self._normalize(key)] = self._normalize_record(record)

                self._index_rebuild()
                self._persist()

            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="import_memories",
                message="Memoria importada correctamente.",
                data=self.memory
            )
        except Exception as exc:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="import_memories",
                message=f"Error al importar: {exc}"
            )

    def backup(self, data: dict | None = None) -> ActionResult:
        """Crea una copia de seguridad de la memoria actual."""
        path = (data.get("path") if data else None) or BACKUP_PATH
        with self._lock:
            self._write_storage(path, self.memory)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="backup",
            message=f"Backup creado en {path}.",
            data={"path": path}
        )

    def restore(self, data: dict | None = None) -> ActionResult:
        """Restaura la memoria desde una copia de seguridad."""
        path = (data.get("path") if data else None) or BACKUP_PATH
        contenido = self._read_storage(path)

        # FIX: se usa "is None" en vez de "not contenido" para distinguir
        # "no existe backup" de "el backup existe pero está vacío ({})",
        # que antes se trataban igual y provocaban un error incorrecto.
        if contenido is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="restore",
                message="No se encontró backup."
            )

        with self._lock:
            self.memory = {self._normalize(key): self._normalize_record(record) for key, record in contenido.items()}
            self._index_rebuild()
            self._persist()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="restore",
            message="Memoria restaurada desde backup."
        )

    def sync(self, data: dict | None = None) -> ActionResult:
        """Fuerza el volcado a disco, haya o no cambios pendientes."""
        wrote = self.save(force=True)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="memory",
            command="sync",
            message="Memoria sincronizada.",
            data={
                "saved": wrote,
                "dirty": self._dirty,
                "last_saved_at": self._last_saved_at,
            }
        )

    def validate(self, data: dict | None = None) -> ActionResult:
        """Valida que el archivo de memoria en disco sea JSON íntegro."""
        path = (data.get("path") if data else None) or MEMORY_PATH
        try:
            with open(path, "r", encoding="utf-8") as file_handle:
                json.load(file_handle)
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="memory",
                command="validate",
                message=f"Archivo {path} válido."
            )
        except FileNotFoundError:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="memory",
                command="validate",
                message=f"El archivo {path} no existe todavía."
            )
        except Exception as exc:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="validate",
                message=f"Archivo corrupto: {exc}"
            )

    def summarize(self) -> str:
        """Resumen en texto plano de toda la memoria (firma original preservada)."""
        if not self.memory:
            return "No tengo recuerdos."
        return "\n".join(f"{key}: {record['value']}" for key, record in self.memory.items())

    # ==================================================
    # 9. UTILIDADES / HELPERS PRIVADOS
    # ==================================================
    def _read_storage(self, path: str) -> dict | None:
        """
        Único punto de LECTURA de almacenamiento. Hoy delega en
        JSONManager; migrar a SQLite/Postgres/Mongo implica reemplazar
        únicamente este método (y `_write_storage`).
        """
        return JSONManager.load(path)

    def _write_storage(self, path: str, data: dict) -> None:
        """Único punto de ESCRITURA de almacenamiento (ver `_read_storage`)."""
        JSONManager.save(path, data)

    def _now(self) -> str:
        return datetime.now().isoformat()

    def _generate_id(self) -> str:
        import uuid
        return uuid.uuid4().hex

    def _normalize(self, key: Any) -> str:
        """Normaliza una clave: castea a str, recorta espacios y colapsa espacios internos."""
        if key is None:
            return ""
        return " ".join(str(key).split())

    def _normalize_category(self, category: Any) -> str:
        if not category or not isinstance(category, str) or not category.strip():
            return DEFAULT_CATEGORY
        return category.strip().lower()

    def _normalize_tag_list(self, items: list | None) -> list[str]:
        """
        Normaliza una lista de tags/aliases: recorta espacios, colapsa
        espacios internos y pasa a minúsculas, descartando vacíos. Se usa
        al crear el registro para que `find_by_tag("Project")` y
        `find_by_tag("project")` encuentren lo mismo.
        """
        normalized = []
        for item in items or []:
            value = self._normalize(item).lower()
            if value:
                normalized.append(value)
        return normalized

    def _clamp_importance(self, importance: Any) -> int:
        try:
            value = int(importance)
        except (TypeError, ValueError):
            value = DEFAULT_IMPORTANCE
        return max(MIN_IMPORTANCE, min(MAX_IMPORTANCE, value))

    def _validate_key(self, key: Any) -> tuple[bool, str | None]:
        if key is None:
            return False, "La clave no puede ser None."
        if not isinstance(key, str):
            return False, "La clave debe ser una cadena de texto."
        if not key.strip():
            return False, "La clave no puede estar vacía."
        return True, None

    def _validate_value(self, value: Any) -> tuple[bool, str | None]:
        if value is None:
            return False, "El valor no puede ser None."
        if isinstance(value, str) and not value.strip():
            return False, "El valor no puede ser una cadena vacía."
        return True, None

    def _validate_key_value(self, key: Any, value: Any) -> bool:
        """
        Helper que consolida el patrón `_validate_key` + `_validate_value`
        repetido en `remember()`/`update()`. No cambia los mensajes de
        error públicos (esos siguen definidos en cada método llamador),
        solo evita duplicar la lógica de validación.
        """
        valid_key, _ = self._validate_key(key)
        if not valid_key:
            return False
        valid_value, _ = self._validate_value(value)
        return valid_value

    def _create_record(
        self,
        value: Any,
        category: str = DEFAULT_CATEGORY,
        importance: int = DEFAULT_IMPORTANCE,
        source: str = "user",
        aliases: list | None = None,
        tags: list | None = None,
    ) -> dict:
        """Centraliza la construcción de un registro de memoria con forma consistente."""
        now = self._now()
        return {
            "id": self._generate_id(),
            "value": value,
            "category": category,
            "created_at": now,
            "updated_at": now,
            "importance": importance,
            "source": source,
            "times_used": 0,
            "last_access": None,
            "aliases": self._normalize_tag_list(aliases),
            "tags": self._normalize_tag_list(tags),
        }

    def _normalize_record(self, raw: Any) -> dict:
        """
        Rellena campos faltantes de un registro cargado desde disco
        (compatibilidad con archivos memory.json de versiones anteriores).
        """
        if not isinstance(raw, dict):
            raw = {"value": raw}

        now = self._now()
        normalized = {
            "id": raw.get("id") or self._generate_id(),
            "value": raw.get("value"),
            "category": self._normalize_category(raw.get("category")),
            "created_at": raw.get("created_at") or now,
            "updated_at": raw.get("updated_at") or now,
            "importance": self._clamp_importance(raw.get("importance", DEFAULT_IMPORTANCE)),
            "source": raw.get("source", "user"),
            "times_used": raw.get("times_used") or 0,
            "last_access": raw.get("last_access"),
            "aliases": self._normalize_tag_list(raw.get("aliases")),
            "tags": self._normalize_tag_list(raw.get("tags")),
        }
        return MemoryRecord(normalized)

    def _touch(self, key: str) -> None:
        """Actualiza el último acceso de una memoria. Solo marca 'dirty' (no escribe a disco)."""
        if key in self.memory:
            self.memory[key]["last_access"] = self._now()
            self.mark_dirty()

    def _increment_usage(self, key: str) -> None:
        """Incrementa el contador de uso de una memoria. Solo marca 'dirty' (no escribe a disco)."""
        if key in self.memory:
            self.memory[key]["times_used"] = self.memory[key].get("times_used", 0) + 1
            self.mark_dirty()

    def _trim_conversation_turns(self) -> None:
        """
        Mantiene como máximo `MAX_CONVERSATION_TURNS` memorias de la
        categoría 'conversation' (las creadas por `remember_turn()`),
        eliminando las más antiguas cuando se supera el límite. Evita que
        memory.json crezca sin control y que `get_relevant_memory()` se
        llene de ruido con cada turno de charla.
        """
        with self._lock:
            keys = list(self._category_index.get("conversation", ()))
            if len(keys) <= MAX_CONVERSATION_TURNS:
                return

            turns = [(key, self.memory[key]) for key in keys if key in self.memory]
            if not turns:
                return
            
            turns.sort(key=lambda kv: kv[1].get("created_at") or "")

            excess = len(turns) - MAX_CONVERSATION_TURNS
            for key, record in turns[:excess]:
                # Verificar que la clave aún existe antes de remover (race condition)
                if key in self.memory:
                    self.memory.pop(key, None)
                    self._index_remove(key, record)

            self._persist()

    # --- Índices internos (categoría / etiquetas) ---------------------
    def _index_add(self, key: str, record: dict) -> None:
        """Agrega `key` a los índices invertidos de categoría y etiquetas según `record`."""
        category = record.get("category", DEFAULT_CATEGORY)
        self._category_index.setdefault(category, set()).add(key)
        for tag in record.get("tags", []) or []:
            self._tag_index.setdefault(tag, set()).add(key)

    def _index_remove(self, key: str, record: dict) -> None:
        """Retira `key` de los índices invertidos de categoría y etiquetas según `record`."""
        category = record.get("category", DEFAULT_CATEGORY)
        bucket = self._category_index.get(category)
        if bucket is not None:
            bucket.discard(key)
            if not bucket:
                del self._category_index[category]

        for tag in record.get("tags", []) or []:
            bucket = self._tag_index.get(tag)
            if bucket is not None:
                bucket.discard(key)
                if not bucket:
                    del self._tag_index[tag]

    def _index_rebuild(self) -> None:
        """Reconstruye ambos índices desde cero a partir de `self.memory`."""
        self._category_index = {}
        self._tag_index = {}
        for key, record in self.memory.items():
            self._index_add(key, record)

    def _category_counts(self) -> dict[str, int]:
        """Cantidad de memorias por categoría, calculada desde el índice invertido."""
        return {category: len(keys) for category, keys in self._category_index.items() if keys}

    # ==================================================
    # 10. SERIALIZACIÓN
    # ==================================================
    def to_dict(self) -> dict:
        with self._lock:
            return {
                "memory": self.memory,
                "dirty": self._dirty,
                "last_saved_at": self._last_saved_at,
                "autosave_enabled": self.autosave_enabled,
            }

    def from_dict(self, data: dict) -> "MemoryManager":
        """
        Reconstruye el estado del manager en RAM a partir de un dict
        (por ejemplo, el resultado de `to_dict()`).

        IMPORTANTE: `from_dict()` solo carga en memoria y marca la
        memoria como "dirty"; NO persiste a disco automáticamente.
        Para escribir el resultado en `memory.json` hay que llamar
        explícitamente a `save()` (o `sync()` / `export()`) después.
        Este comportamiento es intencional: separa "reconstruir estado
        en RAM" de "persistir a disco".
        """
        if not isinstance(data, dict):
            return self

        raw = data.get("memory", {})
        if not isinstance(raw, dict):
            raw = {}

        with self._lock:
            self.memory = {self._normalize(key): self._normalize_record(record) for key, record in raw.items()}
            self._index_rebuild()
            self._last_saved_at = data.get("last_saved_at")
            if "autosave_enabled" in data:
                self.autosave_enabled = bool(data["autosave_enabled"])
            self.mark_dirty()
        return self

    # ==================================================
    # 11. REPRESENTACIÓN
    # ==================================================
    def __len__(self) -> int:
        return len(self.memory)

    def __contains__(self, key: str) -> bool:
        return self._normalize(key) in self.memory

    def __iter__(self):
        return iter(self.memory.items())

    def __repr__(self) -> str:
        return f"<MemoryManager entradas={len(self.memory)} dirty={self._dirty}>"

    # ==================================================
    # MEMORIA PERMANENTE DESDE CONVERSACIÓN
    # ==================================================

    def remember_fact(
        self,
        key: str,
        value: Any,
        category: str = "general",
        importance: int = DEFAULT_IMPORTANCE,
        aliases: list | None = None,
        tags: list | None = None
    ) -> ActionResult:
        """
        Guarda un dato permanente identificado por una clave.
        Pensado para ser utilizado directamente por Conversation/IA.
        """

        return self.remember({
            "key": key,
            "value": value,
            "category": category,
            "importance": importance,
            "source": "conversation",
            "aliases": aliases or [],
            "tags": tags or [],
        })

    # ==================================================
    # PROYECTOS
    # ==================================================

    def remember_project(
        self,
        project_name: str,
        description: str = ""
    ) -> ActionResult:
        """
        Guarda un proyecto como memoria permanente.
        Cada proyecto tiene su propia clave (`project:<nombre>`), lo que
        permite recordar varios proyectos distintos sin pisarse entre sí.
        """

        project_name = self._normalize(project_name)

        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="memory",
                command="remember_project",
                message="No se especificó el nombre del proyecto."
            )

        key = f"project:{project_name.lower()}"

        return self.remember({
            "key": key,
            "value": {
                "name": project_name,
                "description": description
            },
            "category": "projects",
            "importance": 5,
            "source": "conversation",
            "aliases": [
                "proyecto",
                "mi proyecto",
                project_name.lower()
            ],
            "tags": [
                "project",
                "proyecto",
                "ia"
            ]
        })

    def get_project(self, project_name: str) -> dict | None:
        """
        Recupera un proyecto específico.
        """

        if not project_name:
            return None

        key = f"project:{self._normalize(project_name).lower()}"

        record = self.memory.get(key)

        if not record:
            return None

        return record.get("value")
