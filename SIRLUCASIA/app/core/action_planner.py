from app.core.actions import Action


class ActionPlanner:

    def plan(self, message):

        # ==================================================
        # Validación inicial
        # ==================================================

        if not isinstance(message, dict):
            return []

        # Algunos módulos pueden entregar:
        #
        # {
        #     "result": {...}
        # }
        #
        # mientras que otros entregan directamente:
        #
        # {
        #     "module": "...",
        #     "command": "..."
        # }

        data = message.get("result", message)

        if not isinstance(data, dict):
            return []

        print("ACTION PLANNER RECIBE:")
        print(data)
        print(type(data))

        # ==================================================
        # Copia para evitar modificar accidentalmente
        # el diccionario original
        # ==================================================

        data = dict(data)

        # ==================================================
        # TOPIC INICIAL
        # ==================================================

        topic = data.get("topic")

        # ==================================================
        # RESOLVER PARAMETERS DEL PARSER
        # ==================================================

        if (
            "parameters" in data
            and isinstance(data["parameters"], dict)
        ):

            params = data["parameters"]

            # Los grupos deben venir del Parser.
            #
            # Ejemplo:
            #
            # matches = (
            #     "txt",
            #     "prueba",
            #     "hola lucas"
            # )
            #
            groups = data.get("matches", [])

            # Aceptar también tuple
            if isinstance(groups, tuple):
                groups = list(groups)

            resolved = {}

            for key, value in params.items():

                # ==========================================
                # El Parser dejó un índice numérico
                # ==========================================

                if isinstance(value, int):

                    index = value - 1

                    if 0 <= index < len(groups):

                        resolved[key] = groups[index]

                    else:

                        print(
                            f"[ActionPlanner] "
                            f"No pude resolver el parámetro "
                            f"'{key}' con índice {value}."
                        )

                # ==========================================
                # El parámetro ya contiene su valor real
                # ==========================================

                else:

                    resolved[key] = value

            # ==============================================
            # Actualizar parámetros
            # ==============================================

            data["parameters"] = resolved

            # ==============================================
            # Copiar valores al nivel principal
            # ==============================================

            data.update(resolved)

            print("[ActionPlanner] Parámetros resueltos:")
            print(resolved)

        # ==================================================
        # DOCUMENT RENAME
        # ==================================================

        if (
            data.get("module") == "document"
            and data.get("command") == "rename"
        ):

            old_name = (
                data.get("old_name")
                or data.get("topic")
            )

            new_name = data.get("new_name")

            topic = old_name

            # Crear entidad si no existe
            if not isinstance(data.get("entity"), dict):
                data["entity"] = {
                    "type": "document"
                }

            data["entity"]["old_name"] = old_name
            data["entity"]["new_name"] = new_name

        # ==================================================
        # DOCUMENT COPY
        # ==================================================

        elif (
            data.get("module") == "document"
            and data.get("command") == "copy"
        ):

            old_name = (
                data.get("old_name")
                or data.get("topic")
            )

            new_name = data.get("new_name")

            topic = old_name

            # Crear entidad si no existe
            if not isinstance(data.get("entity"), dict):
                data["entity"] = {
                    "type": "document"
                }

            data["entity"]["old_name"] = old_name
            data["entity"]["new_name"] = new_name

        # ==================================================
        # DOCUMENT CREATE
        # ==================================================

        elif (
            data.get("module") == "document"
            and data.get("command") == "create"
        ):

            if data.get("topic"):
                topic = data.get("topic")

            # Asegurar entidad
            if not isinstance(data.get("entity"), dict):
                data["entity"] = {
                    "type": "document"
                }

            data["entity"]["name"] = topic

            if data.get("format"):
                data["entity"]["format"] = data.get("format")

        # ==================================================
        # DOCUMENT READ
        # ==================================================

        elif (
            data.get("module") == "document"
            and data.get("command") == "read"
        ):

            topic = (
                data.get("topic")
                or data.get("filename")
                or data.get("name")
            )

        # ==================================================
        # ACTUALIZAR TOPIC SI EXISTE
        # ==================================================

        if topic is not None:
            data["topic"] = topic

        # ==================================================
        # CREAR ACTION
        # ==================================================

        action = Action(
            module=data.get("module"),
            command=data.get("command"),
            topic=topic,
            entity=data.get("entity"),
            parameters=data,
        )

        print("ACTION PLANNER CREA:")
        print(action)

        return [action]