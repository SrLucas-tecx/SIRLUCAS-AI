from __future__ import annotations

import logging
import json
import random
import os

from typing import Any

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.memory_manager import MemoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.context_manager import ContextManager
from app.core.task_executor import TaskExecutor
from app.modules.project_memory_handler import ProjectMemoryHandler
from app.service.system_manager import SystemManager

# ==================================================
# NUEVA IMPORTACIÓN
# ==================================================
from app.core.brain.brain_manager import BrainManager

system_manager = SystemManager()

logger = logging.getLogger(__name__)


class ConversationManager:
    """Orquestador puro: coordina Memoria, Conocimiento, Contexto y Ejecución de tareas."""

    PROJECT_MEMORY_COMMANDS = frozenset({
        "remember_project",
        "remember_project_description",
        "recall_project",
        "update_project",
        "get_project_details",
        "list_projects",
        "search_project",
        "forget_project",
        "create_project",
        "add_project_detail",
    })

    def __init__(
        self,
        memory: MemoryManager | None = None,
        knowledge: KnowledgeManager | None = None,
        context: ContextManager | None = None,
        task_executor: TaskExecutor | None = None,
        # ==================================================
        # NUEVA DEPENDENCIA INYECTADA
        # ==================================================
        brain_manager: BrainManager | None = None,
    ) -> None:

        self.memory = memory or MemoryManager()
        self.knowledge = knowledge or KnowledgeManager()
        self.context = context or ContextManager()
        self.task_executor = task_executor

        # ==================================================
        # INICIALIZACIÓN DE BRAIN MANAGER
        # ==================================================
        # Si no se inyecta desde fuera, lo creamos pasándole las instancias actuales.
        # ESTO DEBE ADAPTARSE A TU IMPLEMENTACIÓN ACTUAL si tienes un ContextBuilder separado.
        self.brain_manager = brain_manager or BrainManager(
            memory_manager=self.memory,
            knowledge_manager=self.knowledge,
            context_builder=self.context  
        )

        self.project_memory_handler = ProjectMemoryHandler(self.memory)

        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data"
        )
        base_path = os.path.abspath(base_path)

        try:
            with open(os.path.join(base_path, "intents.json"), "r", encoding="utf-8") as f:
                self.intents = json.load(f)
        except FileNotFoundError:
            logger.warning("[ConversationManager] No se encontró 'intents.json'.")
            self.intents = {}

        try:
            with open(os.path.join(base_path, "responses.json"), "r", encoding="utf-8") as f:
                self.responses = json.load(f)
        except FileNotFoundError:
            logger.warning("[ConversationManager] No se encontró 'responses.json'.")
            self.responses = {}

        logger.info(
            "[ConversationManager] Inicializado correctamente "
            "con intents, responses, project memory y BrainManager."
        )

    def execute(self, data: dict) -> Any:
        # ... (Mantienes tu código intacto) ...
        command = data.get("command")
        method = getattr(self, command, None)

        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="conversation",
                command=command,
                message=f"No existe el comando '{command}'.",
                error=f"Comando '{command}' no implementado en ConversationManager.",
            )
        return method(data)

    def process(self, data: dict) -> Any:
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

        # 1. Snapshot del contexto
        context_snapshot = self._get_context_snapshot()

        # ==================================================
        # 2. Acciones de proyecto (deterministas)
        # ==================================================
        project_save_result = self._handle_project_action(data)

        if project_save_result is not None:
            if project_save_result.success:
                logger.info(f"[ConversationManager] Proyecto auto-guardado: {project_save_result.message}")
            response = project_save_result
            
            # Si resolvió por acción, mapeamos vacíos para la estructura
            brain_context_dict = {}
            memory_hits = []

        else:
            # ==================================================
            # 3. BRAIN MANAGER: Análisis, Planificación y Recuperación
            # ==================================================
            # Reemplaza a `self._consult_memory()`. BrainManager decide 
            # de forma inteligente qué fuentes tocar.
            
            brain_ctx = self.brain_manager.process(
                message=message,
                conversation_history=context_snapshot,
                parsed_intent=data
            )
            
            brain_context_dict = brain_ctx.to_dict()
            memory_hits = brain_context_dict.get("memory_data", [])

            # ==================================================
            # 4. Resolver respuesta normal
            # ==================================================
            response = self._resolve_response(
                message=message,
                context=context_snapshot,
                memory_hits=memory_hits,
                raw_data=data,
                brain_context=brain_context_dict # NUEVO: Pasamos toda la estructura
            )

        # 5. Persistir contexto y memoria del turno
        self._persist_context(message, response)
        self._persist_memory(message, response)

        # 6. Guardado Diferido
        save = getattr(self.memory, "save", None)
        if callable(save):
            save()

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
                "brain_context": brain_context_dict # Exponemos la decisión del cerebro
            },
        )

    def talk(self, data: dict) -> ActionResult:
        # ... (Mantienes tu código intacto por compatibilidad) ...
        pass

    def _get_context_snapshot(self) -> dict:
        # ... (Mantienes tu código intacto) ...
        pass

    def _persist_context(self, message: str, response: Any) -> None:
        # ... (Mantienes tu código intacto) ...
        pass

    # ==================================================
    # NOTA: _consult_memory() ya no se usa directamente en process() 
    # porque BrainManager lo absorbió. Puedes eliminarlo o dejarlo
    # por si lo llamas desde otro lado.
    # ==================================================

    def _persist_memory(self, message: str, response: Any) -> None:
        # ... (Mantienes tu código intacto) ...
        pass

    def _handle_project_action(self, rule_result: dict) -> ActionResult | None:
        # ... (Mantienes tu código intacto) ...
        pass

    def _consult_knowledge(self, query: str, context: dict | None) -> Any:
        # ... (Mantienes tu código intacto) ...
        pass

    def _run_task(self, data: dict) -> Any:
        # ... (Mantienes tu código intacto) ...
        pass

    def _resolve_response(
        self,
        message: str,
        context: dict,
        memory_hits: Any,
        raw_data: dict,
        brain_context: dict = None # NUEVO ARGUMENTO
    ) -> Any:

        intent_tag = raw_data.get("rule") or raw_data.get("tag")

        if hasattr(self, "responses") and intent_tag in self.responses:
            return random.choice(self.responses[intent_tag])

        if hasattr(self, "intents"):
            for intent in self.intents.get("intents", []):
                if intent["tag"] == intent_tag:
                    return random.choice(intent["responses"])

        if raw_data.get("command"):
            if raw_data.get("module") == "system":
                from app.service.system_manager import SystemManager
                system_manager = SystemManager()
                
                # Puedes inyectar el brain_context aquí si SystemManager lo soporta
                return system_manager.execute(raw_data)

            else:
                # ==================================================
                # INYECCIÓN DEL BRAIN CONTEXT HACIA EL TASK EXECUTOR
                # ==================================================
                task_payload = {
                    **raw_data,
                    "context": context,
                    "memory": memory_hits,
                    "brain_context": brain_context or {} # TaskExecutor (y luego Ollama) recibe TODO ordenado
                }
                return self._run_task(task_payload)

        # Fallback
        return self._consult_knowledge(
            message,
            {
                "context": context,
                "memory": memory_hits,
                "brain_context": brain_context
            }
        )

    def _fallback_execute(self, target: Any, command: str, data: dict) -> Any:
        # ... (Mantienes tu código intacto) ...
        pass