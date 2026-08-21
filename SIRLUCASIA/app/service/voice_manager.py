import logging
import speech_recognition as sr
import pyttsx3

logger = logging.getLogger(__name__)


class VoiceManager:

    def __init__(self, rate: int = 175, volume: float = 1.0):
        # Se especifica 'sapi5' para evitar errores de comtypes en Windows
        try:
            self.engine = pyttsx3.init('sapi5')
        except Exception:
            self.engine = pyttsx3.init()

        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

        # Configurar voz en español si está disponible
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "spanish" in voice.name.lower() or "es" in voice.id.lower():
                self.engine.setProperty("voice", voice.id)
                break

        self.recognizer = sr.Recognizer()

    def speak(self, text: str) -> None:
        """Convierte texto en voz y lo reproduce."""
        if not text:
            return
        logger.info(f"[VoiceManager] Hablando: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"[VoiceManager] Error al hablar: {e}")

    def listen(self) -> str:
        """Escucha por el micrófono y devuelve el texto reconocido."""
        with sr.Microphone() as source:
            print("\n🎤 Escuchando... (habla ahora)")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("🧠 Procesando audio...")
                text = self.recognizer.recognize_google(audio, language="es-ES")
                print(f"Tú (Voz) > {text}")
                return text
            except sr.WaitTimeoutError:
                print("⚠️ No se detectó voz.")
                return ""
            except sr.UnknownValueError:
                print("⚠️ No logré entender lo que dijiste.")
                return ""
            except sr.RequestError as e:
                logger.error(f"[VoiceManager] Error del servicio de voz: {e}")
                return ""