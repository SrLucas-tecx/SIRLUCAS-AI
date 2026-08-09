class EntityResolver:

    def __init__(self):
        pass

    def resolve(self, data):

        # Verificar que realmente sea un diccionario
        if not isinstance(data, dict):
            return data

        module = data.get("module")
        command = data.get("command")

        # ===============================
        # SYSTEM
        # ===============================
        if module == "system":

            data["entity"] = {
                "type": "program",
                "value": data.get("topic")
            }

        # ===============================
        # DOCUMENT
        # ===============================
        elif module == "document":

            # --------------------------------
            # Renombrar documento
            # --------------------------------
            if command == "rename":

                data["entity"] = {
                    "type": "document",
                    "old_name": data.get("old_name"),
                    "new_name": data.get("new_name")
                }

            # --------------------------------
            # Copiar documento
            # --------------------------------
            elif command == "copy":

                data["entity"] = {
                    "type": "document",
                    "old_name": data.get("old_name"),
                    "new_name": data.get("new_name")
                }

            # --------------------------------
            # Crear documento
            # --------------------------------
            elif command == "create":

                data["entity"] = {
                    "type": "document",
                    "name": data.get("topic"),
                    "format": data.get("format")
                }

            # --------------------------------
            # Resto de documentos
            # --------------------------------
            else:

                data["entity"] = {
                    "type": "document",
                    "name": data.get("topic"),
                    "format": data.get("format")
                }

        # ===============================
        # MEMORY
        # ===============================
        elif module == "memory":

            data["entity"] = {
                "type": "memory",
                "key": data.get("key")
            }

        # ===============================
        # WEB
        # ===============================
        elif module == "web":

            data["entity"] = {
                "type": "search",
                "query": data.get("topic")
            }

        # ===============================
        # KNOWLEDGE
        # ===============================
        elif module == "knowledge":

            data["entity"] = {
                "type": "knowledge",
                "query": data.get("topic")
            }

        return data