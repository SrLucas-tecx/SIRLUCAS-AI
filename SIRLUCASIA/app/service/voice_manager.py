"""VoiceManager — Síntesis y reconocimiento de voz para SIRLUCAS AI.

Motor TTS primario : edge-tts  (Microsoft Edge, online, sin API key)
Motor TTS fallback : pyttsx3   (offline, menor calidad)
STT               : SpeechRecognition + Google (online)
"""

import asyncio
import logging
import os
import tempfile
import threading
import speech_recognition as sr

logger = logging.getLogger(__name__)

# ── Intento importar edge-tts (recomendado) ──────────────────────────────────
try:
    import edge_tts

    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning(
        "[VoiceManager] edge-tts no disponible. Usando pyttsx3 como fallback."
    )

# ── Intento importar pyttsx3 (fallback offline) ──────────────────────────────
try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("[VoiceManager] pyttsx3 no disponible.")

# ── Intento importar pygame para reproducir audio de edge-tts ────────────────
try:
    import pygame

    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# ── Intento importar playsound como alternativa a pygame ─────────────────────
try:
    from playsound import playsound

    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False


class VoiceManager:
    """Gestiona síntesis de voz (TTS) y reconocimiento de voz (STT).

    Orden de preferencia TTS:
      1. edge-tts  (online, alta calidad)
      2. pyttsx3   (offline, fallback)
    """

    # Voz de edge-tts en español (mujer, México)
    EDGE_VOICE = "es-MX-DaliaNeural"

    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self._pyttsx3_engine = None

        # Inicializar pygame mixer si está disponible
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                logger.warning(
                    f"[VoiceManager] pygame.mixer no se pudo inicializar: {e}"
                )

        # Inicializar pyttsx3 si edge-tts no está presente
        if not EDGE_TTS_AVAILABLE and PYTTSX3_AVAILABLE:
            self._init_pyttsx3()

        self.recognizer = sr.Recognizer()
        logger.info(
            "[VoiceManager] Iniciado. "
            f"TTS={'edge-tts' if EDGE_TTS_AVAILABLE else 'pyttsx3' if PYTTSX3_AVAILABLE else 'NINGUNO'}"
        )

    # ── Inicialización de pyttsx3 ─────────────────────────────────────────────

    def _init_pyttsx3(self):
        """Inicializa o reinicia el motor pyttsx3."""
        try:
            try:
                self._pyttsx3_engine = pyttsx3.init("sapi5")
            except Exception:
                self._pyttsx3_engine = pyttsx3.init()

            self._pyttsx3_engine.setProperty("rate", self.rate)
            self._pyttsx3_engine.setProperty("volume", self.volume)

            voices = self._pyttsx3_engine.getProperty("voices")
            for voice in voices:
                name_lower = voice.name.lower()
                id_lower = voice.id.lower()
                if (
                    "spanish" in name_lower
                    or "es_" in id_lower
                    or "\\es\\" in id_lower
                ):
                    self._pyttsx3_engine.setProperty("voice", voice.id)
                    break

        except Exception as e:
            logger.error(f"[VoiceManager] No se pudo inicializar pyttsx3: {e}")
            self._pyttsx3_engine = None

    # ── TTS con edge-tts ──────────────────────────────────────────────────────

    def _speak_edge(self, text: str) -> bool:
        """Sintetiza voz con edge-tts y la reproduce."""
        if not EDGE_TTS_AVAILABLE:
            return False

        tmp_path = None
        try:
            # Crear archivo y cerrar el handle inmediatamente para evitar bloqueos en Windows
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name

            async def _synthesize():
                communicate = edge_tts.Communicate(text, self.EDGE_VOICE)
                await communicate.save(tmp_path)

            try:
                asyncio.run(_synthesize())
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_synthesize())
                loop.close()

            self._play_audio(tmp_path)
            return True

        except Exception as e:
            logger.error(f"[VoiceManager] edge-tts falló: {e}")
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def _play_audio(self, filepath: str):
        """Reproduce el archivo MP3 mediante Pygame o Playsound."""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.unload()  # Libera el archivo para poder borrarlo
                return
            except Exception as e:
                logger.warning(f"[VoiceManager] pygame falló al reproducir: {e}")

        if PLAYSOUND_AVAILABLE:
            try:
                playsound(filepath)
                return
            except Exception as e:
                logger.warning(f"[VoiceManager] playsound falló: {e}")

        logger.error(
            "[VoiceManager] No hay reproductor disponible (instala pygame o playsound)."
        )

    # ── TTS con pyttsx3 ───────────────────────────────────────────────────────

    def _speak_pyttsx3(self, text: str) -> bool:
        """Sintetiza voz con pyttsx3 (fallback offline)."""
        if not PYTTSX3_AVAILABLE:
            return False

        if self._pyttsx3_engine is None:
            self._init_pyttsx3()

        if self._pyttsx3_engine is None:
            return False

        try:
            self._pyttsx3_engine.say(text)
            self._pyttsx3_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(
                f"[VoiceManager] pyttsx3 falló: {e}. Intentando reiniciar engine."
            )
            self._pyttsx3_engine = None
            self._init_pyttsx3()
            if self._pyttsx3_engine:
                try:
                    self._pyttsx3_engine.say(text)
                    self._pyttsx3_engine.runAndWait()
                    return True
                except Exception as e2:
                    logger.error(f"[VoiceManager] pyttsx3 falló tras reinicio: {e2}")
            return False

    # ── Interfaz pública ──────────────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Convierte texto en voz y lo reproduce."""
        if not text or not text.strip():
            return

        logger.info(
            f"[VoiceManager] Hablando: {text[:80]}{'...' if len(text) > 80 else ''}"
        )

        if EDGE_TTS_AVAILABLE and self._speak_edge(text):
            return

        if PYTTSX3_AVAILABLE and self._speak_pyttsx3(text):
            return

        logger.error(
            "[VoiceManager] No se pudo reproducir audio con ningún motor TTS."
        )

    def listen(self) -> str:
        """Escucha por el micrófono de manera síncrona."""
        try:
            with sr.Microphone() as source:
                print("\n🎤 Escuchando... (habla ahora)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                try:
                    audio = self.recognizer.listen(
                        source, timeout=5, phrase_time_limit=10
                    )
                    print("🧠 Procesando audio...")
                    text = self.recognizer.recognize_google(
                        audio, language="es-ES"
                    )
                    print(f"Tú (Voz) > {text}")
                    return text
                except sr.WaitTimeoutError:
                    print("⚠️ No se detectó voz.")
                    return ""
                except sr.UnknownValueError:
                    print("⚠️ No logré entender lo que dijiste.")
                    return ""
                except sr.RequestError as e:
                    logger.error(
                        f"[VoiceManager] Error del servicio de reconocimiento: {e}"
                    )
                    print(
                        "⚠️ Error de conexión con el servicio de reconocimiento de voz."
                    )
                    return ""
        except OSError as e:
            logger.error(f"[VoiceManager] Micrófono no disponible: {e}")
            print("⚠️ No se detectó micrófono. Escribe tu mensaje.")
            return ""

    def listen_with_timeout(self, timeout_seconds: int = 10) -> tuple[str, str]:
        """Escucha por micrófono durante 'timeout_seconds'.

        Si no detecta voz, cambia a modo texto automáticamente.

        Returns:
            tuple: (texto_reconocido, modo_usado)
                   modo_usado puede ser "voice" o "text"
        """
        result = {"text": "", "mode": "voice"}
        voice_done = threading.Event()

        def _listen_thread():
            try:
                with sr.Microphone() as source:
                    print(
                        f"\n🎤 Escuchando... ({timeout_seconds}s, o escribe para omitir)"
                    )
                    self.recognizer.adjust_for_ambient_noise(
                        source, duration=0.5
                    )
                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=timeout_seconds,
                            phrase_time_limit=10,
                        )
                        text = self.recognizer.recognize_google(
                            audio, language="es-ES"
                        )
                        result["text"] = text
                        result["mode"] = "voice"
                        print(f"Tú (Voz) > {text}")
                    except sr.WaitTimeoutError:
                        result["text"] = ""
                        result["mode"] = "text"
                        print(
                            f"\n⏱️ Sin voz en {timeout_seconds}s. Cambiando a texto..."
                        )
                    except sr.UnknownValueError:
                        result["text"] = ""
                        result["mode"] = "text"
                        print("\n⚠️ No entendí. Cambiando a texto...")
                    except sr.RequestError as e:
                        logger.error(f"[VoiceManager] STT error: {e}")
                        result["text"] = ""
                        result["mode"] = "text"
            except OSError:
                result["text"] = ""
                result["mode"] = "text"
                print("\n⚠️ Micrófono no disponible. Cambiando a texto...")
            finally:
                voice_done.set()

        thread = threading.Thread(target=_listen_thread, daemon=True)
        thread.start()
        thread.join()

        return result["text"], result["mode"]

    def stop(self) -> None:
        """Libera recursos de reproducción y síntesis."""
        if self._pyttsx3_engine:
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass
            self._pyttsx3_engine = None

        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass

        logger.info("[VoiceManager] Recursos de voz liberados.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    vm = VoiceManager()
    vm.speak("VoiceManager configurado correctamente.")