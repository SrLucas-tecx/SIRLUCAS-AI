from datetime import datetime
import uuid

class Action:
    def __init__(
        self,
        module,
        command,
        topic=None,        # ← NUEVO
        entity=None,
        parameters=None,
        priority=0
    ):
        self.id = str(uuid.uuid4())
        self.module = module
        self.command = command
        self.topic = topic   # ← NUEVO
        self.entity = entity
        self.parameters = parameters or {}
        self.priority = priority
        self.created_at = datetime.now()
        self.status = "pending"

    # =====================================
    def complete(self):
        self.status = "completed"

    # =====================================
    def fail(self):
        self.status = "failed"

    # =====================================
    def running(self):
        self.status = "running"

    # =====================================
    def to_dict(self):

        data = {
            "id": self.id,
            "module": self.module,
            "command": self.command,
            "topic": self.topic,
            "entity": self.entity,
            "priority": self.priority,
            "status": self.status,
        }

        data.update(self.parameters)

        return data

    # =====================================
    def __repr__(self):
        return (
            f"<Action "
            f"{self.module}.{self.command} "
            f"topic={self.topic} "       # ← NUEVO
            f"status={self.status}>"
        )
