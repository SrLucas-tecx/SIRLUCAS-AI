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

        action = Action(
            module=data.get("module"),
            command=data.get("command"),
            topic=data.get("topic"),
            entity=data.get("entity"),
            parameters=data,
        )

        print("ACTION PLANNER CREA:")
        print(action)

        return [action]