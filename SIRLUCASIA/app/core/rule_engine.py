import re


class RuleEngine:

    def __init__(self, rules):
        self.rules = sorted(
            rules,
            key=lambda r: r.get("priority", 999)
        )

    def match(self, text):

        for rule in self.rules:

            for regex in rule["regex"]:

                match = re.match(regex, text)

                if not match:
                    continue

                result = {
                    "rule": rule["name"],
                    "module": rule["module"],
                    "command": rule["command"]
                }

                # ===============================
                # Copiar todos los campos fijos
                # ===============================
                for key, value in rule.items():

                    if key in [
                        "name",
                        "regex",
                        "module",
                        "command",
                        "priority"
                    ]:
                        continue

                    if not key.endswith("_group"):
                        result[key] = value

                # ===============================
                # Capturar grupos
                # ===============================
                for key, value in rule.items():

                    if not key.endswith("_group"):
                        continue

                    field = key.replace("_group", "")

                    if match.lastindex and value <= match.lastindex:
                        result[field] = match.group(value).strip()

                    elif value == 0:
                        result[field] = match.group(0).strip()

                print(f"[RuleEngine] -> {result}")

                return result

        return None