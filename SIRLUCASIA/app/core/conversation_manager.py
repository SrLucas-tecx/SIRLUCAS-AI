from __future__ import annotations

import logging
import json
import random
import os

from typing import Any

from SIRLUCASIA.app.core.action_result import ActionResult
from SIRLUCASIA.app.core.action_status import ActionStatus
from app.core.memory_manager import MemoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.context_manager import ContextManager
from app.core.task_executor import TaskExecutor
from app.core.project_memory_integration import ProjectMemoryIntegration
from app.service.system_manager import SystemManager


system_manager = SystemManager()

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

        # Inyección de dependencias con defaults
        self.memory = memory or MemoryManager()
        self.knowledge = knowledge or KnowledgeManager()
        self.context = context or ContextManager()
        self.task_executor = task_executor

        # Inicializar integración de proyectos
        self.project_memory = ProjectMemoryIntegration(self.memory)

        # ==================================================
        # Cargar los JSON externos
        # ==================================================

        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data"
        )

        base_path = os.path.abspath(base_path)

        try:
            with open(
                os.path.join(base_path, "intents.json"),
                "r",
                encoding="utf-8"
            ) as f:
                self.intents = json.load(f)

        except FileNotFoundError:
            logger.warning(
                "[ConversationManager] No se encontró "
                "'intents.json'. Se usarán valores por defecto."
            )
            self.intents = {}

        try:
            with open(
                os.path.join(base_path, "responses.json"),
                "r",
                encoding="utf-8"
            ) as f:
                self.responses = json.load(f)

        except FileNotFoundError:
            logger.warning(
                "[ConversationManager] No se encontró "
                "'responses.json'. Se usarán valores por defecto."
            )
            self.responses = {}

        logger.info(
            "[ConversationManager] Inicializado correctamente "
            "con intents, responses y project memory integration."
        )

    # ==================================================
    # Dispatcher
    # ==================================================

    def execute(self, data: dict) -> Any:
        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command=command,
                message=f"No existe el comando '{command}'.",
                error=(
                    f"Comando '{command}' no implementado "
                    "en ConversationManager."
                ),
            )

        return method(data)

    # ==================================================
    # Punto de entrada principal de un turno
    # ==================================================

    def process(self, data: dict) -> Any:
        """
        Orquesta un turno de conversación completo.

        Orden:

            1. Lee el contexto actual.
            2. Consulta memorias relevantes.
            3. Resuelve la respuesta.
            4. Persiste contexto y memoria del turno.
            5. Guarda los cambios pendientes de memoria UNA SOLA VEZ.

        La persistencia de memoria utiliza dirty flag:
        las operaciones internas modifican RAM y marcan la memoria
        como dirty; el guardado físico se realiza al terminar el turno.
        """

        message = data.get("message") or data.get("topic")

        if not message:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="process",
                message="No especificaste un mensaje.",
                error="El campo 'message' es obligatorio.",
            )

        # ==================================================
        # 1. Snapshot del contexto
        # ==================================================

        context_snapshot = self._get_context_snapshot()

        # ==================================================
        # 2. Consultar memorias relevantes
        # ==================================================

        memory_hits = self._consult_memory(
            message,
            context_snapshot
        )

        # ==================================================
        # 3. NUEVO: Auto-guardar proyectos detectados
        # ==================================================
        # Ejecuta RuleEngine para detectar y guardar automáticamente
        # proyectos mencionados en la conversación.
        # Ejemplo: "mi proyecto es SIRLUCAS" → auto-guardado en memory.json
        
        project_save_result = self.project_memory.auto_save_project(message)
        
        if project_save_result and project_save_result.success:
            logger.info(
                f"[ConversationManager] Proyecto auto-guardado: {project_save_result.message}"
            )

        # ==================================================
        # 4. Resolver respuesta
        # ==================================================

        response = self._resolve_response(
            message,
            context_snapshot,
            memory_hits,
            data
        )

        # ==================================================
        # 5. Persistir contexto y memoria del turno
        # ==================================================

        self._persist_context(
            message,
            response
        )

        self._persist_memory(
            message,
            response
        )

        # ==================================================
        # OPCIÓN B - GUARDADO DIFERIDO
        # ==================================================
        #
        # Todas las operaciones de MemoryManager realizadas
        # durante este turno únicamente marcaron `_dirty`.
        #
        # Aquí se realiza UN SOLO guardado físico al finalizar
        # el turno, evitando que remember/update/forget/etc.
        # escriban individualmente en memory.json.
        #
        # ==================================================

        save = getattr(self.memory, "save", None)

        if callable(save):
            save()

        # ==================================================
        # Resultado final
        # ==================================================

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="conversation",
            command="process",
            message="Turno de conversación procesado correctamente.",
            data={
                "response": response,
                "context": context_snapshot,
                "memory": memory_hits,
            },
        )

    # ==================================================
    # Compatibilidad hacia atrás
    # ==================================================

    def talk(self, data: dict) -> ActionResult:
        """
        Se conserva por compatibilidad con integraciones existentes
        que ya llaman a talk().
        """

        topic = data.get("topic")

        if topic is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="talk",
                message="No especificaste un tema.",
                error="Campo 'topic' vacío.",
            )

        response = self._consult_knowledge(
            topic,
            context=None
        )

        if response is None:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="conversation",
                command="talk",
                message="No tengo una respuesta para eso.",
                error=(
                    "No se encontró conocimiento "
                    "para el tema especificado."
                ),
            )

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="conversation",
            command="talk",
            message="Respuesta obtenida.",
            data={
                "response": response
            },
        )

    # ==================================================
    # Helpers privados de orquestación
    # ==================================================

    def _get_context_snapshot(self) -> dict:
        """
        Delega en ContextManager.
        """

        for method_name in (
            "get_context",
            "snapshot",
            "get",
        ):

            method = getattr(
                self.context,
                method_name,
                None
            )

            if callable(method):

                try:
                    return method() or {}

                except TypeError:
                    continue

        return (
            self._fallback_execute(
                self.context,
                "get_context",
                {}
            )
            or {}
        )

    # ==================================================

    def _persist_context(
        self,
        message: str,
        response: Any
    ) -> None:

        """
        Delega en ContextManager.
        """

        payload = {
            "message": message,
            "response": response,
        }

        for method_name in (
            "update",
            "push",
            "append",
        ):

            method = getattr(
                self.context,
                method_name,
                None
            )

            if callable(method):

                try:
                    method(payload)
                    return

                except TypeError:
                    continue

        self._fallback_execute(
            self.context,
            "update",
            payload
        )

    # ==================================================

    def _consult_memory(
        self,
        message: str,
        context: dict
    ) -> Any:

        """
        Delega en MemoryManager.consult().
        """

        consult = getattr(
            self.memory,
            "consult",
            None
        )

        if callable(consult):

            result = consult(
                message,
                context
            )

            return getattr(
                result,
                "data",
                result
            )

        return self._fallback_execute(
            self.memory,
            "consult",
            {
                "text": message,
                "context": context,
            }
        )

    # ==================================================

    def _persist_memory(
        self,
        message: str,
        response: Any
    ) -> None:

        """
        Delega en MemoryManager.remember_turn().
        """

        remember_turn = getattr(
            self.memory,
            "remember_turn",
            None
        )

        if callable(remember_turn):

            remember_turn(
                {
                    "message": message,
                    "response": response,
                }
            )

            return

        self._fallback_execute(
            self.memory,
            "remember_turn",
            {
                "message": message,
                "response": response,
            }
        )

    # ==================================================

    def _consult_knowledge(
        self,
        query: str,
        context: dict | None
    ) -> Any:

        """
        Delega en KnowledgeManager.
        """

        for method_name in (
            "answer",
            "find",
            "lookup",
            "query",
        ):

            method = getattr(
                self.knowledge,
                method_name,
                None
            )

            if callable(method):

                try:

                    if context is not None:
                        return method(
                            query,
                            context
                        )

                    return method(query)

                except TypeError:

                    try:
                        return method(query)

                    except TypeError:
                        continue

        return self._fallback_execute(
            self.knowledge,
            "answer",
            {
                "query": query,
                "context": context,
            }
        )

    # ==================================================

    def _run_task(
        self,
        data: dict
    ) -> Any:

        """
        Delega en TaskExecutor.
        """

        if self.task_executor is None:

            logger.warning(
                "[ConversationManager] "
                "Sin TaskExecutor inyectado: "
                "no se ejecuta la tarea."
            )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="process",
                message=(
                    "No se puede ejecutar la tarea: "
                    "TaskExecutor no disponible."
                ),
                error="TaskExecutor no disponible.",
            )

        for method_name in (
            "run",
            "execute",
            "dispatch",
        ):

            method = getattr(
                self.task_executor,
                method_name,
                None
            )

            if callable(method):

                try:
                    return method(data)

                except TypeError:
                    continue

        return None

    # ==================================================
    # Resolver respuesta
    # ==================================================

    def _resolve_response(
        self,
        message: str,
        context: dict,
        memory_hits: Any,
        raw_data: dict
    ) -> Any:

        intent_tag = (
            raw_data.get("rule")
            or raw_data.get("tag")
        )

        # ==================================================
        # Buscar en responses.json
        # ==================================================

        if (
            hasattr(self, "responses")
            and intent_tag in self.responses
        ):

            return random.choice(
                self.responses[intent_tag]
            )

        # ==================================================
        # Buscar en intents.json
        # ==================================================

        if hasattr(self, "intents"):

            for intent in self.intents.get(
                "intents",
                []
            ):

                if intent["tag"] == intent_tag:

                    return random.choice(
                        intent["responses"]
                    )

        # ==================================================
        # Si hay comando/tarea explícito
        # ==================================================

        if raw_data.get("command"):

            # ==================================================
            # SystemManager
            # ==================================================

            if raw_data.get("module") == "system":

                from app.service.system_manager import SystemManager

                system_manager = SystemManager()

                return system_manager.execute(
                    raw_data
                )

            # ==================================================
            # TaskExecutor
            # ==================================================

            else:

                task_payload = {
                    **raw_data,
                    "context": context,
                    "memory": memory_hits,
                }

                return self._run_task(
                    task_payload
                )

        # ==================================================
        # Fallback: KnowledgeManager
        # ==================================================

        return self._consult_knowledge(
            message,
            {
                "context": context,
                "memory": memory_hits,
            }
        )

    # ==================================================
    # Fallback dispatcher
    # ==================================================

    def _fallback_execute(
        self,
        target: Any,
        command: str,
        data: dict
    ) -> Any:

        """
        Último recurso: si el sub-manager no expone
        el método esperado por nombre, se intenta
        su dispatcher uniforme execute().
        """

        execute = getattr(
            target,
            "execute",
            None
        )

        if not callable(execute):

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="process",
                message=(
                    "No se puede ejecutar la tarea: "
                    "TaskExecutor no disponible."
                ),
                error="TaskExecutor no disponible.",
            )

        try:

            result = execute(
                {
                    "command": command,
                    **data
                }
                if isinstance(data, dict)
                else {
                    "command": command
                }
            )

            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="conversation",
                command="process",
                message="Tarea ejecutada correctamente.",
                data={
                    "result": result
                }
            )

        except Exception:

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command="process",
                message="Error al ejecutar la tarea.",
                error="Error inesperado al ejecutar la tarea.",
            )