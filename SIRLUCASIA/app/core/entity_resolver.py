# ==================================================
# EntityResolver
# Crea entidades según el módulo detectado
# ==================================================

class EntityResolver:

    def __init__(self):
        pass

    def resolve(self, data):
        # Verificar que realmente sea un diccionario
        if not isinstance(data, dict):
            return data

        module = data.get("module")

        # ===============================
        # Caso System
        # ===============================
        if module == "system":
            data["entity"] = {
                "type": "program",
                "value": data.get("topic")
            }

        # ===============================
        # Caso Document
        # ===============================
        elif module == "document":
            data["entity"] = {
                "type": "document",
                "name": data.get("topic"),
                "format": data.get("format")
            }

        # ===============================
        # Caso Memory
        # ===============================
        elif module == "memory":
            data["entity"] = {
                "type": "memory",
                "key": data.get("key")
            }

        # ===============================
        # Caso Web
        # ===============================
        elif module == "web":
            data["entity"] = {
                "type": "search",
                "query": data.get("topic")
            }

        # ===============================
        # Caso Knowledge
        # ===============================
        elif module == "knowledge":
            data["entity"] = {
                "type": "knowledge",
                "query": data.get("topic")
            }

        return data

