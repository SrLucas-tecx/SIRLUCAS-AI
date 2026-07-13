class Router:

    def __init__(self):

        self.modules = {}

    def register(self, name, module):

        self.modules[name] = module

    def route(self, data):

        module_name = data.get("module")

        module = self.modules.get(module_name)

        if module is None:
            print(f"[Router] No existe el módulo '{module_name}'.")
            return None

        return module.execute(data)
    