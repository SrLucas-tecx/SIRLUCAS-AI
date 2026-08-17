import logging
import requests


class OllamaClient:

    def __init__(
        self,
        base_url="http://localhost:11434",
        model="llama3:latest",
        timeout=120
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self):
        """Comprueba si el servidor de Ollama está disponible."""

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            logging.error(f"Ollama no disponible: {e}")
            return False

    def generate(self, prompt):
        """Envía un prompt a Ollama y devuelve la respuesta."""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            return data.get("response", "").strip()

        except requests.exceptions.Timeout:
            logging.error("Timeout al generar respuesta con Ollama")
            return "⚠️ Ollama tardó demasiado en responder."

        except requests.exceptions.ConnectionError:
            logging.error("No se pudo conectar con Ollama")
            return "⚠️ No se pudo conectar con Ollama."

        except requests.exceptions.RequestException as e:
            logging.error(f"Error HTTP en Ollama: {e}")
            return "⚠️ Error de comunicación con Ollama."

        except ValueError as e:
            logging.error(f"Respuesta JSON inválida de Ollama: {e}")
            return "⚠️ Ollama devolvió una respuesta inválida."

        except Exception as e:
            logging.error(f"Error en OllamaClient: {e}")
            return "⚠️ Error al comunicarse con Ollama."