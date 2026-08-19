class PromptManager:
    """Construye prompts breves y coherentes para reducir latencia."""

    def __init__(self):
        self._prompt_cache = {}

    @property
    def personality(self):
        return (
            "Identidad: SIRLUCAS AI, mayordomo personal digital. "
            "Trata al usuario con cortesía, discreción y calidez; usa un tono "
            "sereno, elegante y directo. Puedes decir 'señor' ocasionalmente, "
            "sin exagerarlo. Prioriza soluciones prácticas y respuestas breves."
        )

    @property
    def base_instruction(self):
        return (
            "Responde en español. No inventes acciones ni resultados: las acciones "
            "del sistema las ejecuta el flujo determinista. Si falta información, "
            "indícalo con claridad."
        )

    @property
    def communication_style(self):
        return "Estilo: natural, preciso y sin repeticiones. Explica paso a paso solo cuando sea necesario."

    def build(self, message, context_text):
        """Construye un prompt compacto; menos tokens reduce el tiempo de respuesta."""
        cache_key = hash((message, context_text))
        if cache_key not in self._prompt_cache:
            self._prompt_cache[cache_key] = "\n".join((
                self.base_instruction,
                self.personality,
                self.communication_style,
                f"Contexto: {context_text}",
                f"Usuario: {message}",
                "SIRLUCAS:",
            ))
        return self._prompt_cache[cache_key]

    def clear_cache(self):
        self._prompt_cache.clear()
