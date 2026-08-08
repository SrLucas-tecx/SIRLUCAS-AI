"""
ConversationManager
=====================
Orquestador puro de conversación de SIRLUCAS AI.

Responsabilidad ÚNICA de esta clase: coordinar el flujo de un turno de
conversación llamando a los especialistas correspondientes. NO contiene
lógica de memoria, conocimiento, contexto ni persistencia — toda esa
lógica vive en `MemoryManager`, `KnowledgeManager`, `ContextManager` y
`TaskExecutor` respectivamente. Este módulo solo decide *cuándo* y *en
qué orden* se llama a cada uno.

API pública (compatibilidad preservada)
------------------------------------------
    - execute(data)  -> dispatcher genérico (comportamiento original).
    - process(data)  -> punto de entrada principal de un turno de
                         conversación completo (contexto -> memoria ->
                         conocimiento/tarea -> persistencia).
    - talk(data)      -> se conserva por compatibilidad hacia atrás con
                         quien ya la use; ahora delega en KnowledgeManager
                         en vez de tener su propia base de datos.

Nota de integración / contratos asumidos
------------------------------------------
No tengo visibilidad del código real de `KnowledgeManager`,
`ContextManager` ni `TaskExecutor`, así que asumí una convención de
nombres razonable y consistente con `MemoryManager` (que sí revisamos).
Cada llamada a un sub-manager pasa primero por un helper privado
(`_consult_memory`, `_consult_knowledge`, `_get_context_snapshot`, etc.)
que:
    1. Intenta el método "esperado" según el contrato documentado abajo.
    2. Si no existe, cae de forma segura (sin lanzar excepción) a
       `execute({"command": ...})`, que es el dispatcher uniforme que ya
       usa `MemoryManager` y que probablemente los demás managers también
       implementan.
    3. Si nada de eso existe, devuelve un valor neutro (None / {} / [])
       en vez de romper el flujo.

Esto permite que `ConversationManager` funcione hoy mismo sin conocer las
firmas exactas, y que sea trivial de ajustar en cuanto se confirmen los
nombres reales (ver TODOs puntuales en cada helper).

Contratos asumidos (a confirmar):
    - MemoryManager.consult(query, context)      -> ActionResult  (CONFIRMADO, ya existe)
    - MemoryManager.remember_turn(data)           -> ActionResult  (CONFIRMADO, ya existe)
    - ContextManager.get_context() / .snapshot()  -> dict           (ASUMIDO)
    - ContextManager.update(data) / .push(data)   -> None/ActionResult (ASUMIDO)
    - KnowledgeManager.answer(query, context)     -> str/None       (ASUMIDO)
    - TaskExecutor.run(data) / .execute(data)     -> ActionResult   (ASUMIDO)
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.memory_manager import MemoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.context_manager import ContextManager
from app.core.task_executor import TaskExecutor

logger = logging.getLogger(__name__)


class ConversationManager:
    """Orquestador puro: coordina Memoria, Conocimiento, Contexto y Ejecución de tareas."""

    # ==================================================
    # Inicialización
    # ==================================================
    def __init__(
        self,
        memory: MemoryManager | None = None,
        knowledge: KnowledgeManager | None = None,
        context: ContextManager | None = None,
        task_executor: TaskExecutor | None = None,
    ) -> None:
        # Inyección de dependencias con defaults: permite tanto el uso
        # normal (SIRLUCAS instancia todo) como pruebas unitarias con
        # mocks, sin cambiar la firma pública del constructor.
        self.memory = memory or MemoryManager()
        self.knowledge = knowledge or KnowledgeManager()
        self.context = context or ContextManager()
        # TaskExecutor exige (router, event_bus): no se puede construir
        # uno por defecto. Si no se inyecta, queda en None y `_run_task`
        # simplemente no delega.
        self.task_executor = task_executor

        logger.info("[ConversationManager] Inicializado correctamente.")

    # ==================================================
    # Dispatcher (comportamiento original preservado)
    # ==================================================
    def execute(self, data: dict) -> Any:
        command = data.get("command")
        method = getattr(self, command, None)
        if method is None:
            return f"No existe el comando '{command}'."
        return method(data)

    # ==================================================
    # Punto de entrada principal de un turno de conversación
    # ==================================================
    def process(self, data: dict) -> Any:
        """
        Orquesta un turno de conversación completo. No decide *qué*
        responder ni *cómo* recordar: solo define el orden de llamadas:

            1. Lee el contexto actual (ContextManager).
            2. Consulta memorias relevantes (MemoryManager.consult).
            3. Pide una respuesta a Conocimiento/Ejecución de tareas.
            4. Persiste el contexto y la memoria del turno.
        """
        message = data.get("message") or data.get("topic")
        if not message:
            return None

        context_snapshot = self._get_context_snapshot()
        memory_hits = self._consult_memory(message, context_snapshot)

        response = self._resolve_response(message, context_snapshot, memory_hits, data)

        self._persist_context(message, response)
        self._persist_memory(message, response)

        return response

    # ==================================================
    # Compatibilidad hacia atrás
    # ==================================================
    def talk(self, data: dict) -> Any:
        """
        Se conserva por compatibilidad con integraciones existentes que
        ya llaman a `talk()`. La lógica de "buscar una respuesta para un
        tema" ya NO vive acá: se delega íntegramente a KnowledgeManager.
        """
        topic = data.get("topic")
        if topic is None:
            return None

        response = self._consult_knowledge(topic, context=None)
        return response if response is not None else "No tengo una respuesta para eso."

    # ==================================================
    # Helpers privados de orquestación (sin lógica propia,
    # solo delegación defensiva a cada especialista)
    # ==================================================
    def _get_context_snapshot(self) -> dict:
        """Delega en ContextManager. TODO: confirmar nombre real del método de lectura."""
        for method_name in ("get_context", "snapshot", "get"):
            method = getattr(self.context, method_name, None)
            if callable(method):
                try:
                    return method() or {}
                except TypeError:
                    continue
        return self._fallback_execute(self.context, "get_context", {}) or {}

    def _persist_context(self, message: str, response: Any) -> None:
        """Delega en ContextManager. TODO: confirmar nombre real del método de escritura."""
        payload = {"message": message, "response": response}
        for method_name in ("update", "push", "append"):
            method = getattr(self.context, method_name, None)
            if callable(method):
                try:
                    method(payload)
                    return
                except TypeError:
                    continue
        self._fallback_execute(self.context, "update", payload)

    def _consult_memory(self, message: str, context: dict) -> Any:
        """Delega en MemoryManager.consult(), contrato ya confirmado."""
        consult = getattr(self.memory, "consult", None)
        if callable(consult):
            result = consult(message, context)
            return getattr(result, "data", result)
        return self._fallback_execute(self.memory, "consult", {"text": message, "context": context})

    def _persist_memory(self, message: str, response: Any) -> None:
        """Delega en MemoryManager.remember_turn(), contrato ya confirmado."""
        remember_turn = getattr(self.memory, "remember_turn", None)
        if callable(remember_turn):
            remember_turn({"message": message, "response": response})
            return
        self._fallback_execute(self.memory, "remember_turn", {"message": message, "response": response})

    def _consult_knowledge(self, query: str, context: dict | None) -> Any:
        """Delega en KnowledgeManager. TODO: confirmar nombre real (answer/find/lookup)."""
        for method_name in ("answer", "find", "lookup", "query"):
            method = getattr(self.knowledge, method_name, None)
            if callable(method):
                try:
                    return method(query, context) if context is not None else method(query)
                except TypeError:
                    try:
                        return method(query)
                    except TypeError:
                        continue
        return self._fallback_execute(self.knowledge, "answer", {"query": query, "context": context})

    def _run_task(self, data: dict) -> Any:
        """Delega en TaskExecutor. TODO: confirmar nombre real (run/execute/dispatch)."""
        if self.task_executor is None:
            logger.warning("[ConversationManager] Sin TaskExecutor inyectado: no se ejecuta la tarea.")
            return None

        for method_name in ("run", "execute", "dispatch"):
            method = getattr(self.task_executor, method_name, None)
            if callable(method):
                try:
                    return method(data)
                except TypeError:
                    continue
        return None

    def _resolve_response(self, message: str, context: dict, memory_hits: Any, raw_data: dict) -> Any:
        """
        Decide, de forma puramente orquestadora, a quién le corresponde
        resolver el mensaje: si trae un `command`/`task` explícito se
        delega en TaskExecutor; si no, se consulta a KnowledgeManager
        (que a su vez puede apoyarse en `memory_hits` como contexto).
        """
        if raw_data.get("command") or raw_data.get("task"):
            task_payload = {**raw_data, "context": context, "memory": memory_hits}
            return self._run_task(task_payload)

        return self._consult_knowledge(message, {"context": context, "memory": memory_hits})

    def _fallback_execute(self, target: Any, command: str, data: dict) -> Any:
        """
        Último recurso: si el sub-manager no expone ninguno de los
        métodos "esperados" por nombre, se intenta su dispatcher
        uniforme `execute({"command": ...})` (el mismo contrato que ya
        usa MemoryManager). Nunca lanza excepción hacia arriba.
        """
        execute = getattr(target, "execute", None)
        if not callable(execute):
            return None
        try:
            result = execute({"command": command, **data} if isinstance(data, dict) else {"command": command})
            return getattr(result, "data", result)
        except Exception:
            return None
