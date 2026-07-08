import random

from app.utils.json_manager import JSONManager


class Assistant:
    def __init__(self):
        self.name = "SIRLUCAS AI"
        self.version = "0.1"

        # Cargar las intenciones desde el JSON
        self.intents = JSONManager.load("data/intents.json")

    def start(self):
        self.show_banner()
        self.chat()

    def show_banner(self):
        print("=" * 50)
        print(f"{self.name} - Versión {self.version}")
        print("=" * 50)
        print("¡Qué onda!")
        print("Mi nombre es SIRLUCAS AI :)")

        if self.intents:
            print("Intenciones cargadas correctamente")
        else:
            print("Error al cargar las intenciones")

        print("=" * 50)

    def chat(self):
        while True:
            user_input = input("\nTú > ")

            if user_input.lower() in [
                "salir",
                "exit",
                "quit",
                "bye",
                "adiós"
            ]:
                self.stop()
                break

            response = self.process_message(user_input)
            print(f"\n{self.name} > {response}")

    def process_message(self, message):
        # Verificar si las intenciones se cargaron correctamente
        if self.intents is None:
            return "No pude cargar el archivo intents.json. Revisa que sea un JSON válido."

        # Convertir el mensaje a minúsculas
        message = message.lower()

        # Buscar coincidencias en las intenciones
        for intent in self.intents["intents"]:
            for pattern in intent["patterns"]:
                if pattern.lower() in message:
                    return random.choice(intent["responses"])

        # Si no encuentra coincidencias
        return "Lo siento, todavía estoy aprendiendo."

    def stop(self):
        print(f"\n{self.name} > ¡Hasta luego! 👋")


if __name__ == "__main__":
    assistant = Assistant()
    assistant.start()
    