from app.modules.normalizer import Normalizer
from app.utils.json_manager import JSONManager
from app.core.rule_engine import RuleEngine


class Parser:

    def __init__(self):

        # Normalizador
        self.normalizer = Normalizer()

        # Cargar reglas
        self.rules = JSONManager.load(
            "app/modules/parser_rules.json"
        )

        if self.rules is None:
            self.rules = []

        # Inicializar RuleEngine
        self.rule_engine = RuleEngine(self.rules)

        print("=" * 50)
        print(f"[Parser] {len(self.rules)} reglas cargadas.")
        print("=" * 50)

    def parse(self, message):

        # Normalizar el mensaje
        text = self.normalizer.normalize(message)

        # Buscar una regla
        command = self.rule_engine.match(text)

        if command:

            print(
                f"[Parser] Regla ejecutada: {command['rule']}"
            )

            return command

        # No hubo coincidencias
        return message