from datetime import datetime
import uuid


class Action:

    def __init__(

        self,

        module,

        command,

        entity=None,

        parameters=None,

        priority=0

    ):

        self.id=str(uuid.uuid4())

        self.module=module

        self.command=command

        self.entity=entity

        self.parameters=parameters or {}

        self.priority=priority

        self.created_at=datetime.now()

        self.status="pending"

    # =====================================

    def complete(self):

        self.status="completed"

    # =====================================

    def fail(self):

        self.status="failed"

    # =====================================

    def running(self):

        self.status="running"

    # =====================================

    def to_dict(self):

        return{

            "id":self.id,

            "module":self.module,

            "command":self.command,

            "entity":self.entity,

            "parameters":self.parameters,

            "priority":self.priority,

            "status":self.status

        }

    # =====================================

    def __repr__(self):

        return(

            f"<Action "

            f"{self.module}.{self.command} "

            f"status={self.status}>"

        )