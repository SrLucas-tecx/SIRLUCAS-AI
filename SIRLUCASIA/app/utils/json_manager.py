import json


class JSONManager:

    @staticmethod
    def load(path):

        try:

            with open(path, "r", encoding="utf-8") as file:

                content = file.read().strip()

                if not content:
                    return {}

                return json.loads(content)

        except FileNotFoundError:

            print(f"No existe el archivo '{path}'. Se creará uno nuevo.")
            return {}

        except json.JSONDecodeError as e:

            print("Error en el JSON:")
            print(f"Línea: {e.lineno}")
            print(f"Columna: {e.colno}")
            print(f"Mensaje: {e.msg}")

            return None

    @staticmethod
    def save(path, data):

        try:

            with open(path, "w", encoding="utf-8") as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except Exception as e:

            print(f"Error al guardar '{path}': {e}")
            return False
        
    @staticmethod
    def exists(path):
       try:
        with open(path, "r"):
            return True
       except FileNotFoundError:
        return False