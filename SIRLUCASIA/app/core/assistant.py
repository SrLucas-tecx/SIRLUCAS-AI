import random

from app.core.intent_manager import IntentManager
from app.core.memory_manager import MemoryManager
from app.core.command_manager import CommandManager
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
from app.core.response_formatter import ResponseFormatter
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


class Assistant:

    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"

        # Managers principales
        self.intent_manager = IntentManager()
        self.memory = MemoryManager()
        self.command_manager = CommandManager(self.memory)
        self.context = ContextManager()
        self.history = HistoryManager()
        self.knowledge = KnowledgeManager()
        self.web = WebManager()
        self.system = SystemManager()
        self.document = DocumentManager()
        self.calculator = CalculatorManager()

        # Router
        self.router = Router()
        self.router.register("memory", self.memory)
        self.router.register("knowledge", self.knowledge)
        self.router.register("web", self.web)
        self.router.register("system", self.system)
        self.router.register("document", self.document)
        self.router.register("calculator", self.calculator)
        self.router.register("history", self.history)

        # EventBus + Listeners
        self.event_bus = EventBus()
        self.event_bus.subscribe("action.executed", LoggerListener().handle)

        self.metrics = MetricsListener()   # 👈 instancia persistente
        self.event_bus.subscribe("action.executed", self.metrics.handle)

        self.event_bus.subscribe("action.executed", HistoryListener(self.history).handle)
        self.event_bus.subscribe("action.executed", AIListener().handle)

        # Componentes del Pipeline
        self.entity_resolver = EntityResolver()
        self.reference_resolver = ReferenceResolver(self.context)
        self.context_resolver = ContextResolver()
        self.intent_resolver = IntentResolver()
        self.action_planner = ActionPlanner()
        self.action_optimizer = ActionOptimizer()
        self.task_executor = TaskExecutor(self.router, self.event_bus)

        # Pipeline y Formatter
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
        self.response_formatter = ResponseFormatter()

        # Parser
        self.parser = Parser()

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

    def chat(self):
        while True:
            raw_message = input("\nTú > ")

            if raw_message.lower() in ["salir", "exit", "quit"]:
                self.stop()
                break

            # 🔑 Flujo simplificado
            message = self.parser.parse(raw_message)
            result = self.pipeline.execute(message)
            response = self.response_formatter.format(result)

            print(f"\n{self.name} > {response}")

            # Ejemplo: mostrar métricas en debug
            if self.debug:
                print("[Metrics]", self.metrics.summary())

    def stop(self):
        despedida = self.intent_manager.get_by_tag("despedida")
        if despedida:
            print(f"\n{self.name} > {random.choice(despedida['responses'])}")
        else:
            print(f"\n{self.name} > Hasta luego.")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()
