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

                if match is None:
                    continue

                result = {

                    "rule": rule["name"],
                    "module": rule["module"],
                    "command": rule["command"]

                }

                # ======================================
                # key / value (Memoria)
                # ======================================

                if "key" in rule:

                    result["key"] = rule["key"]

                    if match.lastindex:

                        result["value"] = match.group(1).strip()

                # ======================================
                # Capturar automáticamente
                # topic_group
                # format_group
                # content_group
                # etc.
                # ======================================

                for field, group in rule.items():

                    if not field.endswith("_group"):
                        continue

                    if group <= match.lastindex:

                        name = field.replace("_group", "")

                        result[name] = match.group(group).strip()

                print(f"[RuleEngine] -> {result}")

                return result

        return None
    