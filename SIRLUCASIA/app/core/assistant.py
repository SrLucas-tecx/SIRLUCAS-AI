from collections import defaultdict
import logging
import re

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

    # Segundos de silencio antes de caer automáticamente a texto
    VOICE_TIMEOUT = 10

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        self.debug = True

        # Configuración de voz y lectura
        self.voice_mode = False
        self.read_mode = False
        self.voice_manager = None
        self.last_response = ""

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

        # BrainManager
        self.brain_manager = BrainManager(
            memory_manager=self.memory,
            knowledge_manager=self.knowledge,
            context_builder=self.context_builder
        )

    # =========================================================================
    # ARRANQUE
    # =========================================================================

    def start(self):
        self.show_banner()
        self.chat()

    def show_banner(self):
        print("=" * 60)
        print(f"{self.name} | Versión {self.version}")
        print("=" * 60)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")
        print("Comandos disponibles:")
        print(" - 'voz on/off'      : Chat por voz (micrófono + habla)")
        print(" - 'lectura on/off'  : Modo lectura (teclado + habla)")
        print(" - 'leer' / 'repetir': Releer última respuesta")
        print(f" - Sin voz {self.VOICE_TIMEOUT}s      : Cambia a texto automáticamente")
        print("=" * 60)

    # =========================================================================
    # GESTIÓN DEL VOICE MANAGER
    # =========================================================================

    def _ensure_voice_manager(self) -> bool:
        """Garantiza que VoiceManager esté instanciado (sin duplicados)."""
        if self.voice_manager is not None:
            return True
        try:
            self.voice_manager = VoiceManager()
            return True
        except Exception as e:
            print(f"\n{self.name} > Error inicializando voz: {e}")
            return False

    # =========================================================================
    # EXTRACCIÓN Y LIMPIEZA DE TEXTO
    # =========================================================================

    def _extract_text(self, obj) -> str:
        """Extrae texto plano de objetos, diccionarios o respuestas complejas."""
        if obj is None:
            return ""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, dict):
            for key in ["response", "text", "message", "result", "content", "data"]:
                if key in obj and obj[key]:
                    return self._extract_text(obj[key])
            return str(obj)
        if hasattr(obj, "response"):
            return self._extract_text(getattr(obj, "response"))
        if hasattr(obj, "text"):
            return self._extract_text(getattr(obj, "text"))
        return str(obj)

    def _clean_text_for_speech(self, text: str) -> str:
        """Limpia Markdown, URLs y caracteres especiales para el TTS."""
        if not text:
            return ""
        clean = str(text)
        clean = re.sub(r'```[\s\S]*?```', '', clean)
        clean = re.sub(r'https?://\S+', '', clean)
        clean = re.sub(r'[*_#>`~|\-\+]', ' ', clean)
        clean = re.sub(r'[\{\}\[\]]', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    # =========================================================================
    # CONTROL DE MODOS DE VOZ
    # =========================================================================

    def _toggle_voice(self, enable: bool):
        """Activa o desactiva el modo voz completo (micrófono + habla)."""
        if enable:
            if not self._ensure_voice_manager():
                return
            self.voice_mode = True
            self.read_mode = False
            msg = f"Voz activada. Si no hablo en {self.VOICE_TIMEOUT}s, escribe."
            print(f"\n{self.name} > {msg}")
            self.voice_manager.speak("Voz activada")
        else:
            self.voice_mode = False
            msg = "Voz desactivada. Cambiando a consola de texto."
            print(f"\n{self.name} > {msg}")
            if self.voice_manager:
                self.voice_manager.speak("Voz desactivada")

    def _toggle_read(self, enable: bool):
        """Activa o desactiva el modo lectura (teclado + habla)."""
        if enable:
            if not self._ensure_voice_manager():
                return
            self.read_mode = True
            self.voice_mode = False
            msg = "Modo lectura activado. Escribes por teclado y responderé con voz."
            print(f"\n{self.name} > {msg}")
            self.voice_manager.speak("Modo lectura activado")
        else:
            self.read_mode = False
            msg = "Modo lectura desactivado."
            print(f"\n{self.name} > {msg}")

    # =========================================================================
    # CAPTURA DE ENTRADA — con auto-switch voz → texto
    # =========================================================================

    def _get_input(self) -> str:
        """
        Captura la entrada del usuario.

        En modo voz:
          - Llama a listen_with_timeout(VOICE_TIMEOUT).
          - Si no detecta voz en ese lapso, cae automáticamente a input()
            SIN desactivar voice_mode (el siguiente turno vuelve a escuchar).

        En cualquier otro modo:
          - Input de teclado estándar.
        """
        if self.voice_mode and self.voice_manager:
            text, mode = self.voice_manager.listen_with_timeout(self.VOICE_TIMEOUT)

            if mode == "voice" and text:
                # Voz reconocida correctamente
                return text

            # Sin voz detectada → fallback silencioso a teclado
            try:
                fallback = input("Tú (texto) > ").strip()
                return fallback
            except (EOFError, KeyboardInterrupt):
                return ""

        return input("\nTú > ").strip()

    # =========================================================================
    # REPRODUCCIÓN DE VOZ
    # =========================================================================

    def _speak_response(self, text: str, force: bool = False):
        """
        Reproduce la respuesta limpia en altavoces.

        force=True → reproduce aunque no estemos en modo voz/lectura
                      (usado por el comando 'leer'/'repetir'/'releer').
        """
        if not force and not (self.voice_mode or self.read_mode):
            return

        clean_text = self._clean_text_for_speech(text)
        if not clean_text:
            return

        # VoiceManager ya gestiona reintentos y fallbacks internamente
        if self._ensure_voice_manager():
            self.voice_manager.speak(clean_text)

    # =========================================================================
    # EVENTOS
    # =========================================================================

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

    # =========================================================================
    # BUCLE PRINCIPAL DE CHAT
    # =========================================================================

    def chat(self):
        while True:

            # ── Captura de entrada ────────────────────────────────────────────
            try:
                raw_message = self._get_input()
            except (EOFError, KeyboardInterrupt):
                self.stop()
                break

            if not raw_message:
                continue

            # ── Comandos de salida ────────────────────────────────────────────
            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # ── Comandos de control de voz / lectura ──────────────────────────
            cmd = raw_message.lower().strip()

            if cmd in ["voz on", "activar voz"]:
                self._toggle_voice(True)
                continue

            elif cmd in ["voz off", "desactivar voz"]:
                self._toggle_voice(False)
                continue

            elif cmd in ["lectura on", "activar lectura"]:
                self._toggle_read(True)
                continue

            elif cmd in ["lectura off", "desactivar lectura"]:
                self._toggle_read(False)
                continue

            elif cmd in ["leer", "repetir", "releer"]:
                if self.last_response:
                    print(f"\n{self.name} (Lectura) > {self.last_response}")
                    self._speak_response(self.last_response, force=True)
                else:
                    print(f"\n{self.name} > No hay ninguna respuesta previa para leer.")
                continue

            # ── Procesamiento del mensaje ─────────────────────────────────────
            try:
                # Parser
                message = self.parser.parse(raw_message, self.context)

                # Actualizar contexto global
                self.context.update({
                    **message,
                    "raw_message": raw_message
                })

                module  = message.get("module")
                rule    = message.get("rule")
                command = message.get("command")

                # Memoria de proyectos → flujo determinista
                if module == "memory" and command in self.PROJECT_MEMORY_COMMANDS:
                    result = self.project_memory_handler.handle_rule(message)
                    response = self.response_wrapper.wrap(result, source="deterministic")
                    self._emit_action_event(message, response, "deterministic")

                # Conversación / intent desconocido → Ollama
                elif module == "conversation" or rule == "unknown":
                    try:
                        brain_context = self.brain_manager.process(
                            message=raw_message,
                            conversation_history=self.context,
                            parsed_intent=message
                        )

                        result = self.ai_router.handle(
                            raw_message,
                            context=(
                                brain_context.to_dict()
                                if hasattr(brain_context, "to_dict")
                                else brain_context
                            )
                        )

                        raw_resp = (
                            result.get("response", "No recibí respuesta de Ollama.")
                            if isinstance(result, dict)
                            else str(result)
                        )
                        response = self.response_wrapper.wrap(raw_resp, source="ollama")
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
                    response = self.response_wrapper.wrap(result, source="deterministic")

                # Extraer texto plano
                response_text = self._extract_text(response)

                # Guardar y mostrar respuesta
                self.context.set_answer(response_text)
                self.last_response = response_text

                print(f"\n{self.name} > {response_text}")
                self._speak_response(response_text)

            except Exception as e:
                err_msg = f"Ocurrió un error procesando tu mensaje: {e}"
                print(f"\n{self.name} > {err_msg}")
                self._speak_response(err_msg)

            # ── Debug / métricas ──────────────────────────────────────────────
            if self.debug:
                print("[Metrics]", self.metrics_listener.summary())

    # =========================================================================
    # CIERRE
    # =========================================================================

    def stop(self):
        msg = "Hasta luego."
        print(f"\n{self.name} > {msg}")
        if (self.voice_mode or self.read_mode) and self.voice_manager:
            self.voice_manager.speak(msg)
        # Liberar recursos del engine de voz limpiamente
        if self.voice_manager:
            self.voice_manager.stop()


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()