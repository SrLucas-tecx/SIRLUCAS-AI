import re

from app.modules.normalizer import Normalizer
from app.utils.json_manager import JSONManager


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

        print("=" * 50)
        print(f"[Parser] {len(self.rules)} reglas cargadas.")
        print("=" * 50)

    def _apply_rules(self, message, text):

        # Ordenar reglas por prioridad
        rules = sorted(
            self.rules,
            key=lambda rule: rule.get("priority", 999)
        )

        # Buscar coincidencias
        for rule in rules:

            for regex in rule["regex"]:

                match = re.match(regex, text)

                if not match:
                    continue

                print(f"[Parser] Regla ejecutada: {rule['name']}")

                value = ""

                if match.groups():
                    value = match.group(1).strip()

                return {
                    "module": rule.get("module"),
                    "command": rule.get("command"),
                    "key": rule.get("key"),
                    "value": value
                }

        return None

    def parse(self, message):

        # Normalizar el mensaje
        text = self.normalizer.normalize(message)

        # Aplicar reglas
        data = self._apply_rules(
            message,
            text
        )

        if data:
            return data

        # No hubo coincidencias
        return message