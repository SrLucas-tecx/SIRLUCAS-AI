import pyttsx3

# Forzar la inicialización con el driver sapi5 de Windows
engine = pyttsx3.init('sapi5')

engine.setProperty("rate", 160)
engine.say("Hola, la prueba de voz en SIRLUCAS AI funciona correctamente.")
engine.runAndWait()