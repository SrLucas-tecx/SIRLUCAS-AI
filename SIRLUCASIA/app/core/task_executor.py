class TaskExecutor:

    def __init__(self, router, history):

        self.router = router
        self.history = history

    def execute(self, actions):

        responses = []

        for action in actions:

            response = self.router.route(action.to_dict())

            self.history.add(

                module=action.module,

                command=action.command,

                topic=action.topic

            )

            responses.append(response)

        return responses
    