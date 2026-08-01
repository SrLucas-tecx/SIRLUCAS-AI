from app.core.actions import Action


class ActionPlanner:

    def plan(self, message):

        if not isinstance(message, dict):
            return []

        # Si el parser devuelve "result"
        data = message.get("result", message)

        print("ACTION PLANNER RECIBE:")
        print(data)

        action = Action(
            module=data.get("module"),
            command=data.get("command"),
            topic=data.get("topic"),
            entity=data.get("entity")
        )

        print("ACTION PLANNER CREA:")
        print(action)

        return [action]