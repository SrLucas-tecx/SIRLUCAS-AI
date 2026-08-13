# app/ai/ollama_client.py

import requests
import logging

logging.basicConfig(level=logging.INFO)

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="llama3", timeout=50000000):
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

    def generate(self, prompt):
        """
        Envía un prompt a Ollama y devuelve la respuesta completa.
        """

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
            logging.error("Timeout al conectar con Ollama")
            return "⚠️ Tiempo de espera agotado."

        except requests.exceptions.RequestException as e:
            logging.error(f"Error HTTP en Ollama: {e}")
            return "⚠️ Error de comunicación con Ollama."

        except ValueError as e:
            logging.error(f"Respuesta JSON inválida de Ollama: {e}")
            return "⚠️ Ollama devolvió una respuesta inválida."

        except Exception as e:
            logging.error(f"Error en OllamaClient: {e}")
            return "⚠️ Error al comunicarse con Ollama."