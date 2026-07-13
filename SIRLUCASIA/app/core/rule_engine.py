import re


class RuleEngine:

    def __init__(self, rules):

        self.rules = sorted(
            rules,
            key=lambda rule: rule.get("priority", 999)
        )

    def match(self, text):

        for rule in self.rules:

            for regex in rule["regex"]:

                match = re.match(regex, text)

                if not match:
                    continue

                value = ""

                if match.groups():
                    value = match.group(1).strip()

                return {
                    "module": rule.get("module"),
                    "command": rule.get("command"),
                    "key": rule.get("key"),
                    "value": value,
                    "rule": rule.get("name")
                }

        return None
    