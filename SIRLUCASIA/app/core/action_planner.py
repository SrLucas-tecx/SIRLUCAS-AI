from app.core.actions import Action


class ActionPlanner:

    def plan(self, message):

        if not isinstance(message, dict):
            return []

        data = message.get("result", message)

        if not isinstance(data, dict):
            return []

        print("ACTION PLANNER RECIBE:")
        print(data)
        print(type(data))

        topic = data.get("topic")

        # ==========================================
        # Document rename
        # ==========================================
        if data.get("module") == "document" and data.get("command") == "rename":
            topic = data.get("old_name") or data.get("topic")
            if data.get("entity"):
                data["entity"]["old_name"] = topic

        # ==========================================
        # Document copy
        # ==========================================
        elif data.get("module") == "document" and data.get("command") == "copy":
            topic = data.get("old_name") or data.get("topic")
            if data.get("entity"):
                data["entity"]["old_name"] = topic

        # ==========================================
        # 🔧 CAMBIO: Resolver parámetros de regex (format, topic, content)
        # ==========================================
        if "parameters" in data and isinstance(data["parameters"], dict):
            params = data["parameters"]
            resolved = {}

            # 🔧 CAMBIO: Usar los grupos capturados por el Parser
            # Asegúrate de que el Parser guarde match.groups() en data["matches"]
            groups = data.get("matches", [])

            for k, v in params.items():
                if isinstance(v, int):
                    # 🔧 CAMBIO: Resolver índice contra grupos capturados (base 1)
                    if groups and len(groups) >= v:
                        resolved[k] = groups[v - 1]
                else:
                    resolved[k] = v

            # 🔧 CAMBIO: Copiar los valores resueltos a data
            data.update(resolved)

            # 🔧 CAMBIO: Actualizar topic si se resolvió
            if "topic" in resolved:
                topic = resolved["topic"]

        # ==========================================
        # Crear Action
        # ==========================================
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