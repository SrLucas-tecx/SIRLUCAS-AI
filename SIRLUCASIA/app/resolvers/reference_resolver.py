# ==================================================
# ReferenceResolver
# Resuelve referencias como:
#   lo
#   la
#   él
#   ella
# ==================================================

class ReferenceResolver:

    def __init__(self, context):

        self.context = context

    # ==================================================
    # Resolver referencias
    # ==================================================

    def resolve(self, data):

        if not isinstance(data, dict):
            return data

        topic = data.get("topic")

        if topic is None:
            return data

        topic = topic.lower()

        references = [

            "lo",
            "la",
            "los",
            "las",

            "eso",
            "ese",
            "esa",
            "estos",
            "estas",

            "él",
            "ella",

            "anterior",
            "último",
            "ultimo"

        ]

        if topic not in references:
            return data

        module = data.get("module")

        # ==========================================
        # Sistema
        # ==========================================

        if module == "system":

            program = self.context.stack.last_program()

            if program:
                data["topic"] = program

        # ==========================================
        # Documentos
        # ==========================================

        elif module == "document":

            document = self.context.stack.last_document()

            if document:
                data["topic"] = document

        # ==========================================
        # Web / Knowledge
        # ==========================================

        elif module in ("web", "knowledge"):

            search = self.context.stack.last_search()

            if search:
                data["topic"] = search

        return data