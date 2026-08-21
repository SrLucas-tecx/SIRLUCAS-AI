import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("\n[Ajustando ruido de fondo... Habla en 1 segundo]")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print(">>> SIRLUCAS AI te escucha... ¡Di algo!")
    audio = recognizer.listen(source)

try:
    texto = recognizer.recognize_google(audio, language="es-MX")
    print(f"\nReconocido con éxito: {texto}")
except sr.UnknownValueError:
    print("\nNo se entendió lo que dijiste.")
except Exception as e:
    print(f"\nError con el micrófono: {e}")