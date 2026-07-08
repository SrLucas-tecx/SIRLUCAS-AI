import json


class JSONManager:

    @staticmethod
    def load(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            print(f"  No existe el archivo: {path}")
            return None

        except json.JSONDecodeError as e:
            print(f"   Error en el JSON:")
            print(f"   Línea: {e.lineno}")
            print(f"   Columna: {e.colno}")
            print(f"   Mensaje: {e.msg}")
            return None