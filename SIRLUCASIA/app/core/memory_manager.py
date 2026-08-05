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
persistiendo en disco de inmediato, igual que en la versión anterior, para
no cambiar el comportamiento observable. Sin embargo, el bookkeeping
interno que antes escribía en cada `recall()` (contador de uso, último
acceso) ya NO golpea el disco en cada lectura: solo marca la memoria como
"dirty" (`mark_dirty()`), y el volcado real ocurre en `save()`, `sync()`,
`export()` o `autosave()`. Esto elimina la mayor fuente de I/O redundante
del diseño original, que escribía `memory.json` completo en cada consulta.

Escalabilidad
--------------
Toda la persistencia pasa por dos métodos privados, `_read_storage()` y
`_write_storage()`, que hoy delegan en `JSONManager`. Migrar a SQLite,
PostgreSQL o MongoDB en el futuro implica reemplazar únicamente esos dos
métodos: la API pública (`remember`, `recall`, `search`, etc.) no cambia.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.utils.json_manager import JSONManager
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# 1. CONSTANTES
# ==================================================
MEMORY_PATH = "data/memory.json"
BACKUP_PATH = "data/memory_backup.json"

DEFAULT_CATEGORY = "general"
MIN_IMPORTANCE = 1
MAX_IMPORTANCE = 5
DEFAULT_IMPORTANCE = 2
DEFAULT_FIND_LIMIT = 5


class MemoryManager:
    """Administrador de memoria a largo plazo de SIRLUCAS AI."""

    # ==================================================
    # 2. INICIALIZACIÓN
    # ==================================================
    def __init__(self, autosave_enabled: bool = True) -> None:
        raw_memory = self._read_storage(MEMORY_PATH)

        self.memory: dict[str, dict] = {}
        if isinstance(raw_memory, dict):
            for key, record in raw_memory.items():
                self.memory[self._normalize(key)] = self._normalize_record(record)

        self._dirty: bool = False
        self.autosave_enabled = autosave_enabled
        self._last_saved_at: str | None = None

    # ==================================================
    # 3. DISPATCHER
    # ==================================================
    def execute(self, data: dict) -> ActionResult:
        """
        Punto de entrada uniforme usado por el resto de SIRLUCAS AI
        (Router/TaskExecutor). Nunca lanza excepciones: cualquier fallo
        se envuelve en un ActionResult de error.
        """
        command = data.get("command") if isinstance(data, dict) else None

        if not command:
            return ActionResult(False, ActionStatus.ERROR, "memory", command, "No se especificó un comando.")

        method = getattr(self, command, None)
        if method is None or not callable(method) or command.startswith("_"):
            return ActionResult(False, ActionStatus.ERROR, "memory", command, f"No existe el comando '{command}'.")

        try:
            result = method(data)
        except TypeError:
            try:
                result = method()
            except Exception as exc:
                return ActionResult(False, ActionStatus.ERROR, "memory", command, f"Error ejecutando '{command}': {exc}")
        except Exception as exc:
            return ActionResult(False, ActionStatus.ERROR, "memory", command, f"Error ejecutando '{command}': {exc}")

        if isinstance(result, ActionResult):
            return result

        # Compatibilidad: si un método devuelve un valor "crudo", se
        # envuelve automáticamente para mantener un contrato uniforme.
        return ActionResult(True, ActionStatus.SUCCESS, "memory", command, "OK", result)

    # ==================================================
    # 4. CRUD DE MEMORIA
    # ==================================================
    def remember(self, data: dict) -> ActionResult:
        """Crea o sobreescribe una memoria. (Firma y mensajes sin cambios)."""
        key = self._normalize(data.get("key"))
        value = data.get("value")
        category = self._normalize_category(data.get("category"))
        importance = self._clamp_importance(data.get("importance", DEFAULT_IMPORTANCE))

        valid_key, key_error = self._validate_key(key)
        if not valid_key:
            return ActionResult(False, ActionStatus.ERROR, "memory", "remember", "Clave o valor inválido.")

        valid_value, value_error = self._validate_value(value)
        if not valid_value:
            return ActionResult(False, ActionStatus.ERROR, "memory", "remember", "Clave o valor inválido.")

        record = self._create_record(
            value,
            category=category,
            importance=importance,
            source=data.get("source", "user"),
            aliases=data.get("aliases"),
            tags=data.get("tags"),
        )

        if key in self.memory:
            # Preserva id y fecha de creación originales si la clave ya existía.
            record["id"] = self.memory[key].get("id", record["id"])
            record["created_at"] = self.memory[key].get("created_at", record["created_at"])

        self.memory[key] = record
        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "remember", f"Recordaré que tu {key} es {value}.", record)

    def update(self, data: dict) -> ActionResult:
        """Actualiza el valor (y opcionalmente categoría/importancia) de una memoria existente."""
        key = self._normalize(data.get("key"))
        value = data.get("value")

        valid_key, key_error = self._validate_key(key)
        if not valid_key:
            return ActionResult(False, ActionStatus.ERROR, "memory", "update", "Clave o valor inválido.")

        valid_value, value_error = self._validate_value(value)
        if not valid_value:
            return ActionResult(False, ActionStatus.ERROR, "memory", "update", "Clave o valor inválido.")

        if key not in self.memory:
            return ActionResult(False, ActionStatus.WARNING, "memory", "update", f"No existe '{key}' en memoria.")

        self.memory[key]["value"] = value
        self.memory[key]["updated_at"] = self._now()

        if data.get("category"):
            self.memory[key]["category"] = self._normalize_category(data["category"])
        if data.get("importance") is not None:
            self.memory[key]["importance"] = self._clamp_importance(data["importance"])

        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "update", f"He actualizado tu {key} a {value}.", self.memory[key])

    def forget(self, data: dict) -> ActionResult:
        """Elimina una memoria por clave."""
        key = self._normalize(data.get("key"))

        valid_key, _ = self._validate_key(key)
        if not valid_key:
            return ActionResult(False, ActionStatus.ERROR, "memory", "forget", "No especificaste la memoria a eliminar.")

        if key not in self.memory:
            return ActionResult(False, ActionStatus.WARNING, "memory", "forget", f"No existe '{key}' en memoria.")

        del self.memory[key]
        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "forget", f"He olvidado '{key}'.")

    def remove(self, data: dict) -> ActionResult:
        """Alias histórico de `forget()`."""
        return self.forget(data)

    def exists(self, key: str) -> bool:
        """Indica si una clave existe en memoria (firma original preservada)."""
        return self._normalize(key) in self.memory

    def get(self, key: str) -> dict | None:
        """Devuelve el registro completo de una clave, o None (firma original preservada)."""
        return self.memory.get(self._normalize(key))

    def set(self, key: str, value: Any, category: str = "general", importance: int = 2) -> dict:
        """Crea/sobreescribe una memoria "en frío", sin pasar por remember() (firma original preservada)."""
        key = self._normalize(key)
        record = self._create_record(
            value,
            category=self._normalize_category(category),
            importance=self._clamp_importance(importance),
            source="system",
        )
        self.memory[key] = record
        self.mark_dirty()
        self.save(force=True)
        return record

    def clear(self, data: dict | None = None) -> ActionResult:
        """Elimina TODAS las memorias."""
        removed = len(self.memory)
        self.memory.clear()
        self.mark_dirty()
        self.save(force=True)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "clear", f"Se eliminaron {removed} memorias.", {"removed": removed})

    def clear_category(self, data: dict) -> ActionResult:
        """Elimina todas las memorias de una categoría."""
        category = self._normalize_category(data.get("category"))
        keys = [k for k, v in self.memory.items() if v.get("category") == category]

        for key in keys:
            del self.memory[key]

        if keys:
            self.mark_dirty()
            self.save(force=True)

        status = ActionStatus.SUCCESS if keys else ActionStatus.WARNING
        message = (
            f"Se eliminaron {len(keys)} memorias de la categoría '{category}'."
            if keys
            else f"No había memorias en la categoría '{category}'."
        )
        return ActionResult(bool(keys), status, "memory", "clear_category", message, {"removed": keys})

    def rename(self, data: dict) -> ActionResult:
        """Renombra la clave de una memoria existente."""
        old_key = self._normalize(data.get("old_key") or data.get("key"))
        new_key = self._normalize(data.get("new_key"))

        valid_old, error_old = self._validate_key(old_key)
        if not valid_old:
            return ActionResult(False, ActionStatus.ERROR, "memory", "rename", "No especificaste la memoria a renombrar.")

        valid_new, error_new = self._validate_key(new_key)
        if not valid_new:
            return ActionResult(False, ActionStatus.ERROR, "memory", "rename", "No especificaste el nuevo nombre.")

        if old_key not in self.memory:
            return ActionResult(False, ActionStatus.WARNING, "memory", "rename", f"No existe '{old_key}' en memoria.")
        if new_key in self.memory:
            return ActionResult(False, ActionStatus.ERROR, "memory", "rename", f"Ya existe una memoria llamada '{new_key}'.")

        record = self.memory.pop(old_key)
        record["updated_at"] = self._now()
        self.memory[new_key] = record

        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "rename", f"'{old_key}' ahora se llama '{new_key}'.", record)

    def duplicate(self, data: dict) -> ActionResult:
        """Crea una copia independiente de una memoria bajo una nueva clave."""
        source_key = self._normalize(data.get("key") or data.get("source_key"))
        target_key = self._normalize(data.get("new_key") or data.get("target_key"))

        if source_key not in self.memory:
            return ActionResult(False, ActionStatus.WARNING, "memory", "duplicate", f"No existe '{source_key}' en memoria.")

        valid_target, _ = self._validate_key(target_key)
        if not valid_target:
            return ActionResult(False, ActionStatus.ERROR, "memory", "duplicate", "No especificaste el nombre de la copia.")
        if target_key in self.memory:
            return ActionResult(False, ActionStatus.ERROR, "memory", "duplicate", f"Ya existe una memoria llamada '{target_key}'.")

        record = json.loads(json.dumps(self.memory[source_key], default=str))
        record["id"] = self._generate_id()
        record["created_at"] = self._now()
        record["updated_at"] = record["created_at"]
        record["times_used"] = 0
        record["last_access"] = None

        self.memory[target_key] = record
        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "duplicate", f"'{source_key}' duplicado como '{target_key}'.", record)

    def merge(self, data: dict) -> ActionResult:
        """Combina varias memorias existentes en una sola nueva memoria."""
        keys = data.get("keys") or []
        target_key = self._normalize(data.get("new_key") or data.get("target_key"))

        valid_target, _ = self._validate_key(target_key)
        if not valid_target:
            return ActionResult(False, ActionStatus.ERROR, "memory", "merge", "No especificaste el nombre de la memoria combinada.")

        existing = [self._normalize(k) for k in keys if self._normalize(k) in self.memory]
        if not existing:
            return ActionResult(False, ActionStatus.WARNING, "memory", "merge", "Ninguna de las memorias indicadas existe.")

        combined_value = "; ".join(str(self.memory[k]["value"]) for k in existing)
        category = data.get("category") or self.memory[existing[0]].get("category")
        importance = max(self.memory[k].get("importance", DEFAULT_IMPORTANCE) for k in existing)

        record = self._create_record(
            combined_value,
            category=self._normalize_category(category),
            importance=self._clamp_importance(importance),
            source="merge",
        )
        self.memory[target_key] = record

        for key in existing:
            if key != target_key:
                del self.memory[key]

        self.mark_dirty()
        self.save(force=True)

        return ActionResult(
            True, ActionStatus.SUCCESS, "memory", "merge",
            f"Se combinaron {len(existing)} memorias en '{target_key}'.", record,
        )

    # ==================================================
    # 5. BÚSQUEDAS
    # ==================================================
    def recall(self, data: dict) -> ActionResult:
        """Recupera una memoria por clave (firma y mensajes originales preservados)."""
        key = self._normalize(data.get("key"))

        valid_key, _ = self._validate_key(key)
        if not valid_key:
            return ActionResult(False, ActionStatus.ERROR, "memory", "recall", "No especificaste qué recordar.")

        record = self.memory.get(key)
        if record is None:
            return ActionResult(False, ActionStatus.WARNING, "memory", "recall", f"No recuerdo tu {key}.")

        # Bookkeeping: NO escribe a disco en cada lectura, solo marca "dirty".
        self._increment_usage(key)
        self._touch(key)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "recall", record["value"], record)

    def search(self, data: dict | None = None) -> ActionResult:
        """Búsqueda de texto libre sobre valores y claves (comportamiento original preservado y extendido)."""
        query = (data.get("query", "") if data else "").strip().lower()
        if not query:
            return ActionResult(False, ActionStatus.ERROR, "memory", "search", "No especificaste qué buscar.")

        results = {
            key: record
            for key, record in self.memory.items()
            if query in str(record.get("value", "")).lower() or query in key.lower()
        }

        status = ActionStatus.SUCCESS if results else ActionStatus.WARNING
        message = f"Resultados para '{query}'." if results else f"No encontré resultados para '{query}'."
        return ActionResult(bool(results), status, "memory", "search", message, results)

    def search_text(self, data: dict | None = None) -> ActionResult:
        """Alias explícito de `search()` para búsquedas puramente textuales."""
        result = self.search(data)
        result.command = "search_text"
        return result

    def find_by_category(self, category: str) -> dict:
        category = self._normalize_category(category)
        return {k: v for k, v in self.memory.items() if v.get("category") == category}

    def find_by_tag(self, tag: str) -> dict:
        return {k: v for k, v in self.memory.items() if tag in v.get("tags", [])}

    def find_by_alias(self, alias: str) -> dict:
        return {k: v for k, v in self.memory.items() if alias in v.get("aliases", [])}

    def find_by_importance(self, data: dict | int | None = None) -> dict:
        importance = data.get("importance") if isinstance(data, dict) else data
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
        categorias: dict[str, int] = {}
        for record in self.memory.values():
            cat = record.get("category", DEFAULT_CATEGORY)
            categorias[cat] = categorias.get(cat, 0) + 1

        mas_usadas = sorted(self.memory.items(), key=lambda item: item[1].get("times_used", 0), reverse=True)[:5]
        ultimo_acceso = max(self.memory.items(), key=lambda item: item[1].get("last_access") or "", default=None)

        stats = {
            "total": len(self.memory),
            "categorias": categorias,
            "mas_usadas": mas_usadas,
            "ultimo_acceso": ultimo_acceso,
        }
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "statistics", "Estadísticas de memoria.", stats)

    def summary(self, data: dict | None = None) -> ActionResult:
        """Resumen inteligente en lenguaje natural + estadísticas, listo para mostrarse o pasarse a un LLM."""
        stats_result = self.statistics()
        text = self.summarize()
        payload = {"resumen": text, "estadisticas": stats_result.data}
        message = text if self.memory else "No tengo recuerdos."
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "summary", message, payload)

    def count(self, data: dict | None = None) -> ActionResult:
        """Cantidad total de memorias almacenadas (firma y mensaje originales preservados)."""
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "count", f"Tengo {len(self.memory)} memorias.", {"count": len(self.memory)})

    def most_used(self, data: dict | None = None) -> ActionResult:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("times_used", 0), reverse=True)[:limit]
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "most_used", "Memorias más usadas.", dict(items))

    def least_used(self, data: dict | None = None) -> ActionResult:
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if data else DEFAULT_FIND_LIMIT
        items = sorted(self.memory.items(), key=lambda kv: kv[1].get("times_used", 0))[:limit]
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "least_used", "Memorias menos usadas.", dict(items))

    def categories(self, data: dict | None = None) -> ActionResult:
        """Categorías existentes con su cantidad de memorias."""
        categorias: dict[str, int] = {}
        for record in self.memory.values():
            cat = record.get("category", DEFAULT_CATEGORY)
            categorias[cat] = categorias.get(cat, 0) + 1
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "categories", "Categorías disponibles.", categorias)

    def tags(self, data: dict | None = None) -> ActionResult:
        """Conjunto de todas las etiquetas usadas en memoria."""
        todas: set[str] = set()
        for record in self.memory.values():
            todas.update(record.get("tags", []))
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "tags", "Etiquetas disponibles.", sorted(todas))

    def memory_size(self, data: dict | None = None) -> ActionResult:
        """Tamaño aproximado en bytes que ocupa la memoria serializada."""
        size_bytes = len(json.dumps(self.memory, ensure_ascii=False, default=str).encode("utf-8"))
        return ActionResult(
            True, ActionStatus.SUCCESS, "memory", "memory_size",
            f"La memoria ocupa {size_bytes} bytes.", {"bytes": size_bytes, "entries": len(self.memory)},
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
        Heurística simple de relevancia de una memoria respecto a un texto:
        combina coincidencia de clave/valor/alias/tags con importancia y
        frecuencia de uso. Sirve de base a `rank_memories`/`suggest_memories`
        y está pensada para evolucionar a un scoring semántico real
        (embeddings) sin cambiar su firma pública.
        """
        record = self.memory.get(self._normalize(key))
        if record is None or not text:
            return 0.0

        normalized_text = text.lower()
        value_text = str(record.get("value", "")).lower()

        score = 0.0
        if key.lower() in normalized_text:
            score += 3.0
        if value_text and value_text in normalized_text:
            score += 2.0
        for alias in record.get("aliases", []):
            if str(alias).lower() in normalized_text:
                score += 1.5
        for tag in record.get("tags", []):
            if str(tag).lower() in normalized_text:
                score += 1.0

        score += record.get("importance", DEFAULT_IMPORTANCE) * 0.2
        score += min(record.get("times_used", 0), 10) * 0.05

        return round(score, 3)

    def rank_memories(self, data: dict) -> ActionResult:
        """Ordena todas las memorias por relevancia respecto a un texto dado."""
        text = data.get("text", "") if isinstance(data, dict) else str(data or "")
        limit = data.get("limit", DEFAULT_FIND_LIMIT) if isinstance(data, dict) else DEFAULT_FIND_LIMIT

        scored = [(key, self.score_relevance(key, text), record) for key, record in self.memory.items()]
        scored.sort(key=lambda item: item[1], reverse=True)
        ranked = [{"key": k, "score": s, "record": r} for k, s, r in scored[:limit] if s > 0]

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "rank_memories", "Memorias ordenadas por relevancia.", ranked)

    def suggest_memories(self, text: str = "", context: dict | None = None) -> ActionResult:
        """
        Sugiere las memorias más relevantes para un texto/contexto dado.
        Pensado como punto de integración de alto nivel (ver `consult`).
        """
        query_text = text or (context.get("last_user_message") if isinstance(context, dict) else "") or ""
        ranked = self.rank_memories({"text": query_text, "limit": DEFAULT_FIND_LIMIT})
        message = "Sugerencias de memoria." if ranked.data else "No encontré memorias relevantes."
        return ActionResult(bool(ranked.data), ranked.status, "memory", "suggest_memories", message, ranked.data)

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
        """
        turn_id = data.get("turn_id") or self._generate_id()
        value = data.get("response") or data.get("message") or ""
        if not value:
            return ActionResult(False, ActionStatus.WARNING, "memory", "remember_turn", "El turno no tiene contenido para recordar.")

        return self.remember({
            "key": f"turno:{turn_id}",
            "value": value,
            "category": "conversation",
            "importance": MIN_IMPORTANCE,
        })

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
            return ActionResult(False, ActionStatus.WARNING, "memory", "find_similar", f"No existe '{key}' en memoria.")

        category = record.get("category")
        tags = set(record.get("tags", []))

        candidates = []
        for other_key, other in self.memory.items():
            if other_key == key:
                continue
            overlap = len(tags.intersection(other.get("tags", [])))
            same_category = other.get("category") == category
            score = overlap * 2 + (1 if same_category else 0)
            if score > 0:
                candidates.append((other_key, score, other))

        candidates.sort(key=lambda item: item[1], reverse=True)
        similar = [{"key": k, "score": s, "record": r} for k, s, r in candidates[:limit]]

        message = "Memorias similares encontradas." if similar else "No se encontraron memorias similares."
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "find_similar", message, similar)

    def search_semantic(self, data: dict) -> ActionResult:
        """
        Seam para una futura búsqueda semántica basada en embeddings.
        Mientras no exista un backend vectorial, degrada de forma
        transparente a `search_text()` sin romper el contrato público.
        """
        result = self.search_text(data)
        result.command = "search_semantic"
        return result

    # ==================================================
    # 8. PERSISTENCIA
    # ==================================================
    def save(self, force: bool = False) -> bool:
        """
        Vuelca `self.memory` a disco SOLO si hay cambios pendientes
        (`self._dirty`) o si `force=True`. Devuelve True si escribió.
        """
        if not (self._dirty or force):
            return False

        self._write_storage(MEMORY_PATH, self.memory)
        self._dirty = False
        self._last_saved_at = self._now()
        return True

    def autosave(self, data: dict | None = None) -> ActionResult:
        """Punto de entrada explícito para volcar cambios pendientes (usa el dirty flag)."""
        wrote = self.save(force=False)
        message = "Memoria sincronizada en disco." if wrote else "No había cambios pendientes."
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "autosave", message, {"saved": wrote})

    def mark_dirty(self) -> None:
        """Marca la memoria como modificada, pendiente de persistir."""
        self._dirty = True

    def export(self, data: dict | None = None) -> ActionResult:
        """Exporta la memoria completa a `data/memory.json` (o a `data.path` si se indica)."""
        path = (data.get("path") if data else None) or MEMORY_PATH
        self._write_storage(path, self.memory)
        self._dirty = False
        self._last_saved_at = self._now()
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "export", "Memoria exportada correctamente.", {"path": path})

    def import_memories(self, data: dict | None = None) -> ActionResult:
        """Importa memorias desde un archivo JSON externo, fusionándolas con las actuales."""
        archivo = (data.get("file") if data else None) or MEMORY_PATH
        try:
            with open(archivo, "r", encoding="utf-8") as file_handle:
                contenido = json.load(file_handle)

            if not isinstance(contenido, dict):
                raise ValueError("El archivo no contiene un objeto JSON válido.")

            for key, record in contenido.items():
                self.memory[self._normalize(key)] = self._normalize_record(record)

            self.mark_dirty()
            self.save(force=True)

            return ActionResult(True, ActionStatus.SUCCESS, "memory", "import_memories", "Memoria importada correctamente.", self.memory)
        except Exception as exc:
            return ActionResult(False, ActionStatus.ERROR, "memory", "import_memories", f"Error al importar: {exc}")

    def backup(self, data: dict | None = None) -> ActionResult:
        """Crea una copia de seguridad de la memoria actual."""
        path = (data.get("path") if data else None) or BACKUP_PATH
        self._write_storage(path, self.memory)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "backup", f"Backup creado en {path}.", {"path": path})

    def restore(self, data: dict | None = None) -> ActionResult:
        """Restaura la memoria desde una copia de seguridad."""
        path = (data.get("path") if data else None) or BACKUP_PATH
        contenido = self._read_storage(path)

        if not contenido:
            return ActionResult(False, ActionStatus.ERROR, "memory", "restore", "No se encontró backup.")

        self.memory = {self._normalize(key): self._normalize_record(record) for key, record in contenido.items()}
        self.mark_dirty()
        self.save(force=True)

        return ActionResult(True, ActionStatus.SUCCESS, "memory", "restore", "Memoria restaurada desde backup.")

    def sync(self, data: dict | None = None) -> ActionResult:
        """Fuerza el volcado a disco, haya o no cambios pendientes."""
        self.save(force=True)
        return ActionResult(True, ActionStatus.SUCCESS, "memory", "sync", "Memoria sincronizada.")

    def validate(self, data: dict | None = None) -> ActionResult:
        """Valida que el archivo de memoria en disco sea JSON íntegro."""
        path = (data.get("path") if data else None) or MEMORY_PATH
        try:
            with open(path, "r", encoding="utf-8") as file_handle:
                json.load(file_handle)
            return ActionResult(True, ActionStatus.SUCCESS, "memory", "validate", f"Archivo {path} válido.")
        except FileNotFoundError:
            return ActionResult(False, ActionStatus.WARNING, "memory", "validate", f"El archivo {path} no existe todavía.")
        except Exception as exc:
            return ActionResult(False, ActionStatus.ERROR, "memory", "validate", f"Archivo corrupto: {exc}")

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
            "aliases": list(aliases or []),
            "tags": list(tags or []),
        }

    def _normalize_record(self, raw: Any) -> dict:
        """
        Rellena campos faltantes de un registro cargado desde disco
        (compatibilidad con archivos memory.json de versiones anteriores).
        """
        if not isinstance(raw, dict):
            raw = {"value": raw}

        now = self._now()
        return {
            "id": raw.get("id") or self._generate_id(),
            "value": raw.get("value"),
            "category": self._normalize_category(raw.get("category")),
            "created_at": raw.get("created_at") or now,
            "updated_at": raw.get("updated_at") or now,
            "importance": self._clamp_importance(raw.get("importance", DEFAULT_IMPORTANCE)),
            "source": raw.get("source", "user"),
            "times_used": raw.get("times_used") or 0,
            "last_access": raw.get("last_access"),
            "aliases": raw.get("aliases") or [],
            "tags": raw.get("tags") or [],
        }

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

    # ==================================================
    # 10. SERIALIZACIÓN
    # ==================================================
    def to_dict(self) -> dict:
        return {
            "memory": self.memory,
            "dirty": self._dirty,
            "last_saved_at": self._last_saved_at,
        }

    def from_dict(self, data: dict) -> "MemoryManager":
        raw = data.get("memory", {}) if data else {}
        self.memory = {self._normalize(key): self._normalize_record(record) for key, record in raw.items()}
        self._last_saved_at = data.get("last_saved_at") if data else None
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