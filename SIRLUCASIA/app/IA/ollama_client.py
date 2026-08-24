import logging
import requests
import time
import subprocess
import threading


class OllamaClient:

    def __init__(
        self,
        base_url="http://localhost:11434",
        model="llama3:latest",
        timeout=60,           # REDUCIDO: de 200 → 60s (falla rápido si algo va mal)
        max_tokens=250,       # REDUCIDO: de 300 → 250 (respuestas más concisas)
        temperature=0.3,      # REDUCIDO: de 0.4 → 0.3 (menos "creatividad" = más rápido)
        keep_alive="30m",     # AUMENTADO: de 10m → 30m (modelo en RAM más tiempo)
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.keep_alive = keep_alive
        self.process = None
        self.session = requests.Session()

        # Precalentar el modelo en segundo plano al iniciar
        self._warmup_done = False
        threading.Thread(target=self._warmup, daemon=True).start()

    # ── Precalentamiento del modelo ───────────────────────────────────────────

    def _warmup(self):
        """
        Envía un prompt mínimo al arrancar para cargar el modelo en RAM
        antes de que el usuario haga la primera pregunta real.
        Esto elimina el retraso de ~5-15s de la primera respuesta.
        """
        if not self.is_available():
            return
        try:
            payload = {
                "model": self.model,
                "prompt": "Hola",
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "num_predict": 5,       # Solo 5 tokens para calentar
                    "temperature": 0.1,
                    "num_ctx": 512,
                },
            }
            self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            self._warmup_done = True
            logging.info("[OllamaClient] Modelo precalentado en RAM.")
        except Exception as e:
            logging.warning(f"[OllamaClient] Warmup fallido (no crítico): {e}")

    # ── Servidor ──────────────────────────────────────────────────────────────

    def start_server(self):
        """Arranca Ollama en segundo plano si no está corriendo."""
        if self.is_available():
            print("✅ Ollama ya está corriendo.")
            return
        try:
            self.process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Esperar hasta que el servidor responda (máx 10s)
            for _ in range(10):
                time.sleep(1)
                if self.is_available():
                    print("✅ Ollama iniciado.")
                    return
            print("⚠️ Ollama tardó en iniciar.")
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
                timeout=3          # REDUCIDO: de 5 → 3s
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # ── Generación ────────────────────────────────────────────────────────────

    def generate(self, prompt: str) -> str:
        """Envía un prompt a Ollama y devuelve la respuesta."""

        # Truncar prompts muy largos para no saturar el contexto
        if len(prompt) > 3000:
            prompt = prompt[:3000]
            logging.warning("[OllamaClient] Prompt truncado a 3000 caracteres.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "num_predict": self.max_tokens,
                "temperature": self.temperature,
                "num_ctx": 1024,   # REDUCIDO: de 2048 → 1024 (más rápido, suficiente para chat)
                "num_thread": 4,   # NUEVO: limitar threads evita contención en CPU
                "repeat_penalty": 1.1,  # NUEVO: evita repeticiones sin coste extra
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
            print(f"⏱️ Ollama respondió en {elapsed:.2f}s")

            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

        except requests.exceptions.Timeout:
            logging.error("Timeout esperando respuesta de Ollama")
            return "⚠️ Ollama tardó demasiado. Intenta una pregunta más corta."
        except requests.exceptions.ConnectionError:
            logging.error("Sin conexión con Ollama")
            return "⚠️ No se pudo conectar con Ollama."
        except requests.exceptions.RequestException as e:
            logging.error(f"Error HTTP en Ollama: {e}")
            return "⚠️ Error de comunicación con Ollama."
        except ValueError as e:
            logging.error(f"JSON inválido de Ollama: {e}")
            return "⚠️ Ollama devolvió una respuesta inválida."
        except Exception as e:
            logging.error(f"Error en OllamaClient: {e}")
            return "⚠️ Error al comunicarse con Ollama."