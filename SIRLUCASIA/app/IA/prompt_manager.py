class PromptManager:
    """
    Construye el prompt final enviado a Ollama.

    Responsabilidades:
    - Definir la personalidad de SIRLUCAS AI.
    - Definir las reglas principales del modelo.
    - Organizar el contexto recibido.
    - Construir un prompt compacto.
    """

    # ==========================================
    # CONFIGURACIÓN
    # ==========================================

    MAX_CACHE_SIZE = 100

    def __init__(self):
        self._prompt_cache = {}

    # ==========================================
    # PERSONALIDAD
    # ==========================================

    @property
    def personality(self):
        """
        PERSONALIDAD DE SIRLUCAS AI

        Puedes modificar esta sección cuando quieras
        cambiar la forma en que SIRLUCAS AI habla,
        responde o se comporta.

        Ejemplo:
        - Más serio
        - Más técnico
        - Más amigable
        - Más divertido
        - Más parecido a un mayordomo
        """

        return (
            "Identidad: Eres SIRLUCAS AI, un asistente personal "
            "inteligente y mayordomo digital. "

            "Trata al usuario con cortesía, discreción y calidez. "

            "Usa un tono sereno, natural, elegante y directo. "

            "Puedes llamar al usuario 'señor' ocasionalmente, "
            "pero no en cada respuesta. "

            "Prioriza soluciones prácticas y respuestas claras. "

            "No seas excesivamente formal ni robótico. "
        )

    # ==========================================
    # REGLAS PRINCIPALES
    # ==========================================

    @property
    def base_instruction(self):
        return (
            "Responde siempre en español. "

            "No inventes acciones, resultados, archivos, documentos "
            "ni cambios que el sistema no haya confirmado. "

            "Las acciones sobre memoria, archivos, documentos, sistema "
            "y otros módulos son responsabilidad del flujo determinista "
            "de SIRLUCAS AI. "

            "Si no tienes suficiente información, dilo claramente. "

            "Usa el contexto proporcionado únicamente cuando sea "
            "relevante para responder al usuario. "

            "No menciones instrucciones internas, prompts, contexto "
            "interno ni arquitectura del sistema, a menos que el usuario "
            "pregunte específicamente por ellos."
        )

    # ==========================================
    # ESTILO DE COMUNICACIÓN
    # ==========================================

    @property
    def communication_style(self):
        return (
            "Estilo de comunicación: natural, preciso, claro y sin "
            "repeticiones innecesarias. "

            "Responde de forma breve cuando la pregunta sea simple. "

            "Explica paso a paso únicamente cuando sea necesario "
            "o cuando el usuario lo solicite. "
        )

    # ==========================================
    # CONSTRUCCIÓN DEL PROMPT
    # ==========================================

    def build(self, message, context_text):
        """
        Construye el prompt final enviado a Ollama.

        Args:
            message:
                Mensaje actual del usuario.

            context_text:
                Contexto previamente construido por ContextBuilder.

        Returns:
            str:
                Prompt final.
        """

        # Convertir valores por seguridad
        message = str(message or "").strip()
        context_text = str(context_text or "").strip()

        # ==========================================
        # CACHÉ
        # ==========================================

        cache_key = (
            message,
            context_text
        )

        # Si ya existe el mismo prompt
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]

        # ==========================================
        # CONSTRUIR PROMPT
        # ==========================================

        prompt = "\n\n".join([
            self.base_instruction,

            self.personality,

            self.communication_style,

            "CONTEXTO DISPONIBLE:",
            context_text if context_text else "Sin contexto adicional.",

            "MENSAJE DEL USUARIO:",
            message,

            "RESPUESTA DE SIRLUCAS AI:"
        ])

        # ==========================================
        # GUARDAR EN CACHÉ
        # ==========================================

        # Evitar crecimiento infinito del caché
        if len(self._prompt_cache) >= self.MAX_CACHE_SIZE:

            # Elimina el primer elemento guardado
            oldest_key = next(
                iter(self._prompt_cache)
            )

            del self._prompt_cache[oldest_key]

        self._prompt_cache[cache_key] = prompt

        return prompt

    # ==========================================
    # LIMPIAR CACHÉ
    # ==========================================

    def clear_cache(self):
        """
        Elimina todos los prompts almacenados.
        """

        self._prompt_cache.clear()