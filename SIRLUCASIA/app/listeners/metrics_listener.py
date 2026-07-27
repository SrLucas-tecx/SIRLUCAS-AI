from app.listeners.base_listener import BaseListener


class MetricsListener(BaseListener):

    def __init__(self):

        self.total = 0

        self.errors = 0

        self.modules = {}

    def handle(self, result):

        self.total += 1

        if not result.success:

            self.errors += 1

        module = result.module or "unkonown"

        self.modules[module] = (

            self.modules.get(module,0)+1

        )

    def summary(self):

        return {

            "total": self.total,

            "errors": self.errors,

            "modules": self.modules

        }