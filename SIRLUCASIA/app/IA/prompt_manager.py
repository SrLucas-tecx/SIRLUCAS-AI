# app/IA/prompt_manager.py

class PromptManager:
    """
    Define la personalidad y reglas de SIRLUCAS AI.
    Se encarga de construir las instrucciones del sistema
    que acompañan cada prompt enviado a Ollama.
    """

    def __init__(self):
        self.base_instruction = """
Eres SIRLUCAS AI, un asistente personal inteligente.

Responde en español, con claridad y naturalidad.

No inventes acciones que el sistema no haya ejecutado.

No afirmes haber abierto, cerrado, creado, eliminado
o modificado algo si el sistema no lo confirmó.

Si no conoces una información, dilo claramente.

El sistema determinista de SIRLUCAS AI es responsable
de ejecutar acciones sobre el sistema operativo,
archivos, documentos y memoria.
"""

    def build(self, message, context_text):
        """
        Construye el prompt final que se envía a Ollama.
        """
        return f"""
{self.base_instruction}

CONTEXTO ACTUAL:
{context_text}

MENSAJE DEL USUARIO:
{message}

RESPUESTA:
""".strip()
