from collections import defaultdict
import logging

from app.core.memory_manager import MemoryManager
from app.core.chat_manager import ChatManager
from app.modules.parser import Parser
from app.core.context_manager import ContextManager
from app.core.history_manager import HistoryManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.web_manager import WebManager
from app.core.calculator_manager import CalculatorManager
from app.service.system_manager import SystemManager
from app.service.document_manager import DocumentManager
from app.core.router import Router
from app.core.task_pipeline import TaskPipeline
from app.core.entity_resolver import EntityResolver
from app.resolvers import ReferenceResolver
from app.core.context_resolver import ContextResolver
from app.core.intent_resolver import IntentResolver
from app.core.action_planner import ActionPlanner
from app.core.action_optimizer import ActionOptimizer
from app.core.task_executor import TaskExecutor
from app.core.event_bus import EventBus
from app.core.logger_listener import LoggerListener
from app.listeners.metrics_listener import MetricsListener
from app.listeners.history_listener import HistoryListener
from app.listeners.ai_listener import AIListener
from app.IA.ai_router import AIRouter
from app.IA.context_builder import ContextBuilder
from app.IA.response_wrapper_1 import ResponseWrapper
from app.modules.project_memory_handler import ProjectMemoryHandler
from app.core.brain.brain_manager import BrainManager

# Importación de VoiceManager desde app/service/
from app.service.voice_manager import VoiceManager


class ActionEventPayload:
    """
    Envoltorio compatible con atributos dot-notation (.module, .success, etc.)
    que esperan los Listeners del EventBus.
    """
    def __init__(self, message: dict, response: str, source: str, success: bool = True):
        parsed = message if isinstance(message, dict) else {}
        self.module = parsed.get("module") or source or "conversation"
        self.command = parsed.get("command") or "talk"
        self.rule = parsed.get("rule") or "unknown"
        self.success = success
        self.result = response
        self.response = response
        self.source = source
        self.raw_message = parsed.get("raw_message", "")
        self.message = parsed.get("text") or self.raw_message
        self.data = parsed


class Assistant:

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

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        self.debug = True

        # Configuración del servicio de voz
        self.voice_mode = False
        self.voice_manager = None

        # Managers
        self.memory = MemoryManager()
        self.context = ContextManager()
        self.history = HistoryManager()
        self.knowledge = KnowledgeManager()
        self.web = WebManager()
        self.system = SystemManager()
        self.document = DocumentManager()
        self.calculator = CalculatorManager()
        self.conversation = ChatManager()

        # Router determinista
        self.router = Router(context_manager=self.context)
        self.router.register("memory", self.memory)
        self.router.register("knowledge", self.knowledge)
        self.router.register("web", self.web)
        self.router.register("system", self.system)
        self.router.register("document", self.document)
        self.router.register("calculator", self.calculator)
        self.router.register("history", self.history)

        # EventBus
        self.event_bus = EventBus()
        self.logger_listener = LoggerListener()
        self.metrics_listener = MetricsListener()
        self.history_listener = HistoryListener(self.history)
        self.ai_listener = AIListener()

        self.event_bus.subscribe("action.executed", self.logger_listener.handle)
        self.event_bus.subscribe("action.executed", self.metrics_listener.handle)
        self.event_bus.subscribe("action.executed", self.history_listener.handle)
        self.event_bus.subscribe("action.executed", self.ai_listener.handle)

        # Pipeline
        self.entity_resolver = EntityResolver()
        self.reference_resolver = ReferenceResolver(self.context)
        self.context_resolver = ContextResolver()
        self.intent_resolver = IntentResolver()
        self.action_planner = ActionPlanner()
        self.action_optimizer = ActionOptimizer()
        self.task_executor = TaskExecutor(
            self.router,
            self.event_bus
        )

        self.pipeline = TaskPipeline(
            entity_resolver=self.entity_resolver,
            reference_resolver=self.reference_resolver,
            context_resolver=self.context_resolver,
            context_manager=self.context,
            intent_resolver=self.intent_resolver,
            planner=self.action_planner,
            optimizer=self.action_optimizer,
            executor=self.task_executor
        )

        # Parser + IA generativa
        self.parser = Parser()
        self.ai_router = AIRouter()
        self.context_builder = ContextBuilder()
        self.response_wrapper = ResponseWrapper()
        self.project_memory_handler = ProjectMemoryHandler(self.memory)

        # Inicialización de BrainManager
        self.brain_manager = BrainManager(
            memory_manager=self.memory,
            knowledge_manager=self.knowledge,
            context_builder=self.context_builder
        )

    def start(self):
        self.show_banner()
        self.chat()

    def show_banner(self):
        print("=" * 60)
        print(f"{self.name} | Versión {self.version}")
        print("=" * 60)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")
        print("Escribe 'voz on' o 'voz off' para alternar la voz.")
        print("=" * 60)

    def _toggle_voice(self, enable: bool):
        """Activa o desactiva la interacción por voz."""
        if enable:
            if not self.voice_manager:
                try:
                    self.voice_manager = VoiceManager()
                except Exception as e:
                    print(f"\n{self.name} > Error activando voz: {e}")
                    return

            self.voice_mode = True
            msg = "Voz activada. Te escucho."
            print(f"\n{self.name} > {msg}")
            self.voice_manager.speak("Voz activada")
        else:
            self.voice_mode = False
            msg = "Voz desactivada. Cambiando a consola de texto."
            print(f"\n{self.name} > {msg}")
            if self.voice_manager:
                self.voice_manager.speak("Voz desactivada")

    def _get_input(self) -> str:
        """Captura voz si el modo está activo; de lo contrario, pide texto."""
        if self.voice_mode and self.voice_manager:
            text = self.voice_manager.listen()
            if text:
                return text
            print("💡 (Puedes escribir directamente si no usas micrófono)")

        return input("\nTú > ").strip()

    def _speak_response(self, text: str):
        """Reproduce la respuesta en altavoces si la voz está encendida."""
        if self.voice_mode and self.voice_manager:
            self.voice_manager.speak(text)

    def _emit_action_event(self, message, response, source, success=True):
        try:
            payload = ActionEventPayload(
                message=message,
                response=response,
                source=source,
                success=success
            )
            self.event_bus.publish("action.executed", payload)
        except Exception as e:
            if self.debug:
                print(f"[EventBus] No se pudo publicar el evento: {e}")

    def chat(self):
        while True:
            try:
                raw_message = self._get_input()
            except (EOFError, KeyboardInterrupt):
                self.stop()
                break

            if not raw_message:
                continue

            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # Comandos de activación/desactivación manual
            cmd = raw_message.lower().strip()
            if cmd in ["voz on", "activar voz"]:
                self._toggle_voice(True)
                continue
            elif cmd in ["voz off", "desactivar voz"]:
                self._toggle_voice(False)
                continue

            try:
                # Parser
                message = self.parser.parse(
                    raw_message,
                    self.context
                )

                # Actualizar contexto global
                self.context.update({
                    **message,
                    "raw_message": raw_message
                })

                module = message.get("module")
                rule = message.get("rule")
                command = message.get("command")

                # Reglas de proyectos → memoria persistente
                if (
                    module == "memory"
                    and command in self.PROJECT_MEMORY_COMMANDS
                ):
                    result = self.project_memory_handler.handle_rule(message)
                    response = self.response_wrapper.wrap(
                        result,
                        source="deterministic"
                    )
                    self._emit_action_event(message, response, "deterministic")

                # Módulos que requieren Inteligencia / Ollama
                elif module == "conversation" or rule == "unknown":
                    try:
                        brain_context = self.brain_manager.process(
                            message=raw_message,
                            conversation_history=self.context,
                            parsed_intent=message
                        )

                        result = self.ai_router.handle(
                            raw_message,
                            context=brain_context.to_dict() if hasattr(brain_context, "to_dict") else brain_context
                        )

                        raw_resp = result.get("response", "No recibí respuesta de Ollama.") if isinstance(result, dict) else str(result)
                        response = self.response_wrapper.wrap(
                            raw_resp,
                            source="ollama"
                        )
                        self._emit_action_event(message, response, "ollama", success=True)

                    except Exception as e:
                        response = self.response_wrapper.wrap(
                            f"Tuve un problema hablando con el modelo de IA: {e}",
                            source="ollama_error"
                        )
                        self._emit_action_event(message, response, "ollama_error", success=False)

                # Comando determinista → Pipeline
                else:
                    result = self.pipeline.execute(message)
                    response = self.response_wrapper.wrap(
                        result,
                        source="deterministic"
                    )

                # Guardar respuesta
                self.context.set_answer(response)

                # Mostrar y hablar la respuesta
                print(f"\n{self.name} > {response}")
                self._speak_response(response)

            except Exception as e:
                err_msg = f"Ocurrió un error procesando tu mensaje: {e}"
                print(f"\n{self.name} > {err_msg}")
                self._speak_response(err_msg)

            # Debug
            if self.debug:
                print(
                    "[Metrics]",
                    self.metrics_listener.summary()
                )

    def stop(self):
        msg = "Hasta luego."
        print(f"\n{self.name} > {msg}")
        if self.voice_mode and self.voice_manager:
            self.voice_manager.speak(msg)


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()