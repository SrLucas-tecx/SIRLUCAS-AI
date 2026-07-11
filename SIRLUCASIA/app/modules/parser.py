class Parser:

    def __init__(self):

        self.rules =[
            {
            "patterns": [
                    "mi nombre es",
                    "me llamo"
                ],
                "command": "remember",
                "key": "nombre"
            }
        ]
                     

    def parse(self, message):

        text = message.lower().strip()

        # Guardar nombre
        if text.startswith("mi nombre es "):

            for rule in self.rules:
                for pattern in rule["patterns"]:

                 if text.startswith(pattern):

                  value = message[len(pattern):].strip()

                  return (
                     f"{rule['command']} "
                     f"{rule['key']} "
                     f"{value}"
                )
            return message
            #value = message[13:].strip()

            #return f"remember nombre {value}"
            

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