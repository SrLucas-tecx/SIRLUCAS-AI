#print("ESTE ES MI PARSER")

import re
from app.utils.json_manager import JSONManager


class Parser:

    def __init__(self):

        # Cargar reglas
        self.rules = JSONManager.load("app/modules/parser_rules.json")

        print("=" * 50)
        print("DEBUG PARSER")
        print("self.rules =", self.rules)
        print("type =", type(self.rules))
        print("=" * 50)

        if self.rules is None:
            self.rules = []

        print(f"[Parser] {len(self.rules)} reglas cargadas.")

    def _apply_rules(self, message, text):

        for rule in self.rules:

            for regex in rule["regex"]:

                match = re.match(regex, text)

                if not match:
                    continue

                print(f"[Parser] Regla ejecutada: {rule['name']}")

                # Si la regla necesita guardar un valor
                if "key" in rule:

                    value = ""

                    if match.groups():
                        value = match.group(1).strip()

                    return (
                        f"{rule['command']} "
                        f"{rule['key']} "
                        f"{value}"
                    ).strip()

                # Si la regla no necesita valor
                return rule["command"]

        return None

    def parse(self, message):

        # Limpiar espacios
        message = message.strip()
        message = re.sub(r"\s+", " ", message)

        # Texto para comparar
        text = message.lower()

        command = self._apply_rules(message, text)

        if command:
            return command

        return message