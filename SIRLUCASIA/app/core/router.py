class Router:

    def __init__(self):

        self.modules = {}

    def register(self, name, module):

        self.modules[name] = module

    def dispatch(self, module_name, command):

        module = self.modules.get(module_name)

        if module is None:
            return None

        return module.execute(command)
    