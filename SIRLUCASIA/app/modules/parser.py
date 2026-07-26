from app.modules.normalizer import Normalizer
from app.utils.json_manager import JSONManager
from app.core.rule_engine import RuleEngine


class Parser:

    def __init__(self):
        # Inicializar normalizador
        self.normalizer = Normalizer()

        # Cargar reglas desde JSON
        self.rules = JSONManager.load("app/modules/parser_rules.json")
        if self.rules is None:
            self.rules = []

        # Inicializar RuleEngine con las reglas cargadas
        self.rule_engine = RuleEngine(self.rules)

        print("=" * 50)
        print(f"[Parser] {len(self.rules)} reglas cargadas.")
        print("=" * 50)

    def parse(self, message, context=None):
        # Paso 1: Normalizar el mensaje
        text = self.normalizer.normalize(message)
        print(f"[Parser] Texto normalizado: {text}")

        # Paso 2: Buscar coincidencia en las reglas
        result = self.rule_engine.match(text)
        print(f"[Parser] Resultado del RuleEngine: {result}")

        # Paso 3: Si no hay coincidencia, devolver el mensaje original
        if result is None:
            return {"raw_message": message, "normalized": text, "rule": None}

        # =====================================
        # CONTEXTO INTELIGENTE
        # =====================================
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

        print(f"[Parser] Regla ejecutada: {result.get('rule', 'Ninguna')}")

        # Paso 4: Devolver resultado enriquecido
        return {
            "raw_message": message,
            "normalized": text,
            "result": result,
        }
