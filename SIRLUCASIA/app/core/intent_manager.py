import random

from app.utils.json_manager import JSONManager


class IntentManager:

    def __init__(self):

        self.intents = JSONManager.load("data/intents.json")

    def process(self, message):

        if self.intents is None:
            return "No pude cargar intents.json."

        message = message.lower()

        for intent in self.intents["intents"]:

            for pattern in intent["patterns"]:

                if pattern.lower() in message:

                    return random.choice(intent["responses"])

        return "Lo siento, todavía estoy aprendiendo."

    def get_by_tag(self, tag):

        if self.intents is None:
            return None

        for intent in self.intents["intents"]:

            if intent["tag"] == tag:

                return intent

        return None