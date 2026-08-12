# app/ai/ollama_client.py

import requests
import logging

logging.basicConfig(level=logging.INFO)

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3", timeout=30):
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def is_available(self):
        """Verifica si Ollama está corriendo."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Ollama no disponible: {e}")
            return False

    def generate(self, prompt, context=None):
        """
        Envía un prompt a Ollama y recibe la respuesta.
        - prompt: texto del usuario
        - context: opcional, diccionario con info relevante
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
        }
        if context:
            payload["context"] = context

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            logging.error("Timeout al conectar con Ollama")
            return "⚠️ Tiempo de espera agotado."
        except Exception as e:
            logging.error(f"Error en OllamaClient: {e}")
            return "⚠️ Error al comunicarse con Ollama."
