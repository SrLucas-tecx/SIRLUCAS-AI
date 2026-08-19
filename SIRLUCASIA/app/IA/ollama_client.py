import logging
import requests
import time
import subprocess


class OllamaClient:

    def __init__(
        self,
        base_url="http://localhost:11434",
        model="llama3:latest",
        timeout=120,
        max_tokens=250,
        temperature=0.4,
        keep_alive="10m",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.keep_alive = keep_alive
        self.process = None  # referencia al proceso Ollama
        self.session = requests.Session()

    def start_server(self):
        """Arranca Ollama en segundo plano si no está corriendo."""
        try:
            # Lanza el servidor Ollama en segundo plano
            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(2)  # espera breve para que arranque
            print("✅ Ollama iniciado en segundo plano.")
        except Exception as e:
            logging.error(f"No se pudo iniciar Ollama: {e}")

    def stop_server(self):
        """Detiene el servidor Ollama si lo lanzamos desde aquí."""
        if self.process:
            self.process.terminate()
            self.process = None
            print("🛑 Ollama detenido.")

    def is_available(self):
        """Comprueba si el servidor de Ollama está disponible."""
        try:
            response = self.session.get(
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
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
                "num_ctx": 2048,
            },
        }

        try:
            start_time = time.time()

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            elapsed = time.time() - start_time
            print(f"⏱️ Tiempo de respuesta: {elapsed:.2f} segundos")

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
