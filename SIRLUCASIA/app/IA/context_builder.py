# app/IA/context_builder.py

class ContextBuilder:
    """
    Construye el contexto que se envía a Ollama.
    Filtra solo lo relevante del ContextManager.
    """

    def build(self, context_manager):
        context = {}

        # Ejemplo: tomar datos del ContextManager
        context["program"] = getattr(context_manager, "programa_activo", None)
        context["document"] = getattr(context_manager, "documento_activo", None)
        context["topic"] = getattr(context_manager, "tema", None)
        context["history"] = getattr(context_manager, "historial", [])

        # Aquí puedes añadir más campos según tu arquitectura
        return context
