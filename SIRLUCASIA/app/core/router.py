class Router:

    def __init__(self):

        self.modules = {}

    def register(self, name, module):
        name=name.lower()

        self.modules[name] = module

        print(f"[Router] Módulo registrado -> {name}")

    def route(self, data):

        if not isinstance(data, dict):
            return None

        module_name = data.get("module","").lower()
        

        if module_name is None:
            print("[Router] El comando no especifica un módulo.")
            return None

        module = self.modules.get(module_name)

        if module is None:
            print(f"[Router] No existe el módulo '{module_name}'.")
            return None

        return module.execute(data)