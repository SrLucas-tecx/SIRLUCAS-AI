import logging
import re

logger = logging.getLogger(__name__)


class RuleEngine:

    def __init__(self, rules):
        if not isinstance(rules, list):
            logger.warning(
                "[RuleEngine] Reglas inválidas; se utilizará una lista vacía."
            )
            rules = []

        # Ordenar reglas por prioridad
        self.rules = sorted(
            (
                rule
                for rule in rules
                if isinstance(rule, dict)
            ),
            key=lambda rule: rule.get("priority", 999)
        )

    def match(self, text):

        if not isinstance(text, str):
            logger.warning(
                "[RuleEngine] Texto inválido para match: %r",
                text
            )
            return None

        for rule in self.rules:

            for regex in rule.get("regex", []):

                if not isinstance(regex, str):
                    logger.warning(
                        "[RuleEngine] Regex inválido en regla '%s': %r",
                        rule.get("name"),
                        regex
                    )
                    continue

                try:
                    match = re.fullmatch(regex, text)

                except re.error as e:
                    logger.error(
                        "[RuleEngine] Regex inválido en regla '%s': %s",
                        rule.get("name"),
                        e
                    )
                    continue

                if not match:
                    continue

                # ===============================
                # Resultado base
                # ===============================
                result = {
                    "rule": rule.get("name"),
                    "module": rule.get("module"),
                    "command": rule.get("command")
                }

                # ===============================
                # Copiar campos fijos
                # ===============================
                for key, value in rule.items():
                    if key in ["name", "regex", "module", "command", "priority"]:
                        continue
                    if not key.endswith("_group"):
                        result[key] = value

                # ===============================
                # Capturar grupos dinámicos
                # ===============================
                for key, value in rule.items():
                    if not key.endswith("_group"):
                        continue

                    field = key.replace("_group", "")

                    if not isinstance(value, int):
                        logger.warning(
                            "[RuleEngine] Grupo inválido en regla '%s': %r",
                            rule.get("name"),
                            value
                        )
                        continue

                    if value == 0:
                        result[field] = match.group(0).strip()
                    elif match.lastindex and value <= match.lastindex:
                        captured = match.group(value)
                        if captured is not None:
                            result[field] = captured.strip()

                # Guardar los grupos originales para depuración
                result["matches"] = match.groups()

                logger.debug("[RuleEngine] -> %s", result)

                return result  # ✅ Aquí devolvemos el resultado al encontrar coincidencia

        return None  # ✅ Si no hubo coincidencias, devolvemos None
