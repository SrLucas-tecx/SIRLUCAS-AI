class ActionResult:

    def __init__(

        self,

        success,

        message,

        data=None

    ):

        self.success=success

        self.message=message

        self.data=data or {}

    def __bool__(self):

        return self.success

    def __repr__(self):

        return(

            f"<ActionResult "

            f"success={self.success}>"

        )