from app.modules.normalizer import Normalizer
from app.utils.json_manager import JSONManager
from app.core.rule_engine import RuleEngine


class Parser:
    """
    Parser principal de SIRLUCAS AI.

    Responsabilidades:
    - Normalizar el mensaje.
    - Ejecutar las reglas de parser_rules.json.
    - Aplicar información del contexto cuando sea necesario.
    - Devolver un resultado uniforme al resto del sistema.

    El Parser NO ejecuta acciones ni modifica la memoria.
    """

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

    def parse(self, message, context=None):

        # ==================================================
        # VALIDACIÓN
        # ==================================================

        if message is None:
            return {
                "rule": "unknown",
                "module": "conversation",
                "command": "unknown",
                "topic": "",
                "raw_message": message,
                "normalized": ""
            }

        # ==================================================
        # NORMALIZACIÓN
        # ==================================================

        text = self.normalizer.normalize(str(message))

        print(f"[Parser] Texto normalizado: {text}")

        # ==================================================
        # EJECUCIÓN DEL RULE ENGINE
        # ==================================================

        result = self.rule_engine.match(text)

        print(
            f"[Parser] Resultado del RuleEngine: {result}"
        )

        # ==================================================
        # MENSAJE DESCONOCIDO
        # ==================================================

        if result is None:

            result = {
                "rule": "unknown",
                "module": "conversation",
                "command": "unknown",
                "topic": text,
                "raw_message": message,
                "normalized": text
            }

        else:

            # Nos aseguramos de no modificar directamente
            # información que pudiera venir del RuleEngine.
            result = dict(result)

            result.setdefault("raw_message", message)
            result.setdefault("normalized", text)

            # ==================================================
            # CONTEXTO
            # ==================================================

            if context is not None:

                # --------------------------------------------------
                # DOCUMENTOS
                # --------------------------------------------------

                if (
                    result.get("module") == "document"
                    and "topic" not in result
                    and callable(getattr(context, "document", None))
                ):

                    document = context.document()

                    if document is not None:
                        result["topic"] = document

                # --------------------------------------------------
                # SISTEMA
                # --------------------------------------------------

                elif (
                    result.get("module") == "system"
                    and "topic" not in result
                    and callable(getattr(context, "program", None))
                ):

                    program = context.program()

                    if program is not None:
                        result["topic"] = program

                # --------------------------------------------------
                # KNOWLEDGE / WEB
                # --------------------------------------------------

                elif (
                    result.get("module") in ["knowledge", "web"]
                    and "topic" not in result
                    and callable(getattr(context, "search", None))
                ):

                    search = context.search()

                    if search is not None:
                        result["topic"] = search

        # ==================================================
        # INFORMACIÓN DEL PROYECTO
        # ==================================================

        # Si una regla devuelve project_name, conservamos
        # explícitamente el dato para que ConversationManager
        # pueda enviarlo a MemoryManager.
        if "project_name" in result:

            project_name = result.get("project_name")

            if project_name:
                result["project_name"] = str(
                    project_name
                ).strip()

        # ==================================================
        # RESULTADO FINAL
        # ==================================================

        print(
            f"[Parser] Regla ejecutada: "
            f"{result.get('rule')}"
        )

        return result