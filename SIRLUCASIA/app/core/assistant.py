import random

from app.utils.json_manager import JSONManager


class Assistant:

    def __init__(self):

        self.name = "SIRLUCAS AI"
        self.version = "0.1"

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

            message = input("\nTú > ")

            if message.lower() in [
                "salir",
                "exit",
                "quit"
            ]:
                self.stop()
                break

            response = self.process_message(message)

            print(f"\n{self.name} > {response}")

    def process_message(self, message):

        if self.intents is None:
            return "No pude cargar intents.json."

        message = message.lower()

        for intent in self.intents["intents"]:

            if any(pattern.lower() in message for pattern in intent["patterns"]):

                return random.choice(intent["responses"])

        return "Lo siento, todavía estoy aprendiendo."

    def get_intent_by_tag(self, tag):

        if self.intents is None:
            return None

        for intent in self.intents["intents"]:

            if intent["tag"] == tag:
                return intent

        return None

    def stop(self):

        despedida = self.get_intent_by_tag("despedida")

        if despedida:
            print(f"\n{self.name} > {random.choice(despedida['responses'])}")
        else:
            print(f"\n{self.name} > Hasta luego.")
            
            