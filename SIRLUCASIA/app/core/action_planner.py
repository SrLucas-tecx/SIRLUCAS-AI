from app.core.actions import Action


class ActionPlanner:

    def __init__(self):

        pass

    # ======================================

    def plan(self, message):

        if not isinstance(message, dict):

            return []

        action = Action(

            module=message.get("module"),

            command=message.get("command"),

            entity=message.get("entity")

        )

        return [action]