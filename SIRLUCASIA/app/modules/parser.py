from app.modules.normalizer import Normalizer
from app.utils.json_manager import JSONManager
from app.core.rule_engine import RuleEngine


class Parser:

    def __init__(self):

        self.normalizer = Normalizer()

        self.rules = JSONManager.load(
            "app/modules/parser_rules.json"
        )

        if self.rules is None:
            self.rules = []

        self.rule_engine = RuleEngine(self.rules)

        print("=" * 50)
        print(f"[Parser] {len(self.rules)} reglas cargadas.")
        print("=" * 50)

    def parse(self, message, context=None):

        text = self.normalizer.normalize(message)

        print(f"[Parser] Texto normalizado: {text}")

        result = self.rule_engine.match(text)

        print(f"[Parser] Resultado del RuleEngine: {result}")

        # ===============================
        # MENSAJE DESCONOCIDO
        # ===============================
        if result is None:

            return {
                "rule": "unknown",
                "module": "conversation",
                "command": "unknown",
                "topic": text,
                "raw_message": message,
                "normalized": text
            }

        # ===============================
        # CONTEXTO
        # ===============================

        if context is not None:

            if (
                result["module"] == "document"
                and "topic" not in result
                and context.document() is not None
            ):
                result["topic"] = context.document()

            elif (
                result["module"] == "system"
                and "topic" not in result
                and context.program() is not None
            ):
                result["topic"] = context.program()

            elif (
                result["module"] in ["knowledge", "web"]
                and "topic" not in result
                and context.search() is not None
            ):
                result["topic"] = context.search()

        print(
            f"[Parser] Regla ejecutada: {result.get('rule')}"
        )

        return result