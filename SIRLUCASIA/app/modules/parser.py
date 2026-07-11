class Parser:

    def __init__(self):

        self.rules = {
            "mi nombre es": "remember nombre",
            "me llamo": "remember nombre",
            "como me llamo": "recall nombre",
            "cómo me llamo": "recall nombre"
        }

    def parse(self, message):

        text = message.lower().strip()

        # Guardar nombre
        if text.startswith("mi nombre es "):

            value = message[13:].strip()

            return f"remember nombre {value}"

        if text.startswith("me llamo "):

            value = message[9:].strip()

            return f"remember nombre {value}"

        # Recuperar nombre
        if text in [
            "como me llamo",
            "cómo me llamo",
            "¿como me llamo?",
            "¿cómo me llamo?"
        ]:

            return "recall nombre"

        # Si no encontró ninguna regla,
        # devuelve el mensaje original.
        return message