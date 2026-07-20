from app.database.base_database import BaseDatabase


# ==================================================
# ConversationDatabase
# Frases comunes del asistente
# ==================================================

class ConversationDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            "hola":
                "¡Hola! ¿En qué puedo ayudarte?",

            "buenos dias":
                "¡Buenos días!",

            "buenas tardes":
                "¡Buenas tardes!",

            "buenas noches":
                "¡Buenas noches!",

            "gracias":
                "De nada.",

            "adios":
                "Hasta luego.",

            "quien eres":
                "Soy SIRLUCAS AI.",

            "como estas":
                "Estoy funcionando correctamente."

        }
    
    def last(self, amount=10):
        
        return self.data[-amount:]