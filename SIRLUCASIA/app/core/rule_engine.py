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

                if "key" in rule:

                    result["key"] = rule["key"]

                    if match.groups():
                        result["value"] = match.group(1).strip()

                if "topic_group" in rule:

                    result["topic"] = match.group(
                        rule["topic_group"]
                    ).strip()
                    print(result)

                return result

        return None