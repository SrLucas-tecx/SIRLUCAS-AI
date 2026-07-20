class Router:

    def __init__(self):

        self.modules = {}

    # ==========================================
    # Registrar módulos
    # ==========================================
    def register(self, name, module):

        name = name.lower()

        self.modules[name] = module

        print(f"[Router] Módulo registrado -> {name}")

    # ==========================================
    # Router principal
    # ==========================================
    def route(self, data):

        if not isinstance(data, dict):
            return None

        module_name = data.get("module", "").lower()

        if not module_name:

            print("[Router] No se especificó ningún módulo.")

            return None

        # ==========================================
        # CASO ESPECIAL:
        # abrir aplicación o documento
        # ==========================================

        if module_name == "system" and data.get("command") == "open":

            system = self.modules.get("system")
            document = self.modules.get("document")

            if system:

                response = system.open(data)

                # Si sí encontró la aplicación
                if not response.startswith("No conozco"):

                    return response

            # Si no era aplicación intentamos abrir documento
            if document:

                return document.open(data)

            return "No existe ningún módulo para abrir documentos."

        # ==========================================
        # Ruteo normal
        # ==========================================

        module = self.modules.get(module_name)

        if module is None:

            print(f"[Router] No existe el módulo '{module_name}'.")

            return None

        return module.execute(data)