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


class Assistant:

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"
        self.debug = True

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
        #self.memory.remember_project("Silukitas")

        # Router determinista
        self.router = Router()
        self.router.register("memory", self.memory)
        self.router.register("knowledge", self.knowledge)
        self.router.register("web", self.web)
        self.router.register("system", self.system)
        self.router.register("document", self.document)
        self.router.register("calculator", self.calculator)
        self.router.register("history", self.history)
        self.router.register("conversation", self.conversation)

        # EventBus
        self.event_bus = EventBus()
        self.logger_listener = LoggerListener()
        self.metrics_listener = MetricsListener()
        self.history_listener = HistoryListener(self.history)
        self.ai_listener = AIListener()

        

        self.event_bus.subscribe(
            "action.executed", self.logger_listener.handle
        )
        self.event_bus.subscribe(
            "action.executed", self.metrics_listener.handle
        )
        self.event_bus.subscribe(
            "action.executed", self.history_listener.handle
        )
        self.event_bus.subscribe(
            "action.executed", self.ai_listener.handle
        )
        

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

    def start(self):
        self.show_banner()
        self.chat()

    def show_banner(self):
        print("=" * 60)
        print(f"{self.name} | Versión {self.version}")
        print("=" * 60)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")
        print("=" * 60)

    # ==================================================
    # CHAT
    # ==================================================

    def chat(self):
        while True:
            try:
                raw_message = input("\nTú > ").strip()
            except (EOFError, KeyboardInterrupt):
                self.stop()
                break

            if not raw_message:
                continue

            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # Parser
            message = self.parser.parse(
                raw_message,
                self.context
            )

            # Actualizar contexto
            self.context.update({
                **message,
                "raw_message": raw_message
            })

            module = message.get("module")
            rule = message.get("rule")

            # Conversación → Ollama
            if module == "conversation":
                context = self.context_builder.build(
                    self.context,
                    self.memory
                )

                result = self.ai_router.handle(
                    raw_message,
                    context=context
                )

                response = self.response_wrapper.wrap(
                    result.get(
                        "response",
                        "No recibí respuesta de Ollama."
                    ),
                    source="ollama"
                )

            # Mensaje desconocido → Ollama
            elif rule == "unknown":
                context = self.context_builder.build(
                    self.context,
                    self.memory
                )

                result = self.ai_router.handle(
                    raw_message,
                    context=context
                )

                response = self.response_wrapper.wrap(
                    result.get(
                        "response",
                        "No recibí respuesta de Ollama."
                    ),
                    source="ollama"
                )

            # Comando determinista → Pipeline
            else:
                result = self.pipeline.execute(message)

                response = self.response_wrapper.wrap(
                    result,
                    source="deterministic"
                )

            # Guardar respuesta
            self.context.set_answer(response)

            # Mostrar respuesta
            print(f"\n{self.name} > {response}")

            # Debug
            if self.debug:
                print(
                    "[Metrics]",
                    self.metrics_listener.summary()
                )

    def stop(self):
        print(f"\n{self.name} > Hasta luego.")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()