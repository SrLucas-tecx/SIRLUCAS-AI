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
                # old_name_group
                # new_name_group
                # etc.
                # ======================================

                for field, group in rule.items():

                    if not field.endswith("_group"):
                        continue

                    name = field.replace("_group", "")

                    # Si existe el grupo, lo captura
                    if match.lastindex and group <= match.lastindex:

                        result[name] = match.group(group).strip()

                    # Si NO existen grupos y el grupo es 0,
                    # toma toda la coincidencia
                    elif group == 0:

                        result[name] = match.group(0).strip()

                print(f"[RuleEngine] -> {result}")

                return result

        return None