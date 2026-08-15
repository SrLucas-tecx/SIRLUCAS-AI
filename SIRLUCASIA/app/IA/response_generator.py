# app/IA/response_generator.py

class ResponseGenerator:
    """
    Convierte la salida de Ollama en una respuesta clara.
    Puede formatear, enriquecer o simplificar el texto.
    """

    def format(self, ollama_response):
        if not ollama_response:
            return "No recibí respuesta de Ollama."

        # Si la respuesta viene como dict con 'response'
        if isinstance(ollama_response, dict):
            return ollama_response.get("response", "Respuesta vacía.")

        # Si es texto plano
        return str(ollama_response).strip()
