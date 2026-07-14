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

        print("\n===== REGLAS CARGADAS =====")

        for rule in self.rules:
            print(f"- {rule['name']}")

        print("===========================\n")

    def parse(self, message):

        text = self.normalizer.normalize(message)

        print(f"[Normalizer] -> {text}")

        result = self.rule_engine.match(text)

        print(f"[RuleEngine] -> {result}")

        if result:

            print(f"[Parser] Regla ejecutada: {result['rule']}")

            return result

        return message