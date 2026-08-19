class ContextBuilder:
    """
    Construye un contexto controlado para Ollama.

    - Usa ContextManager para contexto de corto plazo.
    - Limita el historial a los últimos 8 turnos.
    - Integra memoria relevante desde MemoryManager.
    """

    MAX_HISTORY = 4
    MAX_MEMORIES = 5
    MAX_MEMORY_CHARS = 500

    def build(self, context_manager, memory_manager=None):

        if context_manager is None:
            return {}

        # ==========================================
        # CONTEXTO DE CORTO PLAZO
        # ==========================================

        history = context_manager.conversation()

        if not history:
            history = []

        history = history[-self.MAX_HISTORY:]

        context = {
            "topic": context_manager.topic(),
            "module": context_manager.module(),
            "command": context_manager.command(),
            "program": context_manager.program(),
            "document": context_manager.document(),
            "search": context_manager.search(),
            "task": context_manager.task(),
            "goal": context_manager.goal(),

            "conversation_mode": (
                context_manager.conversation_mode
            ),

            "last_user_message": (
                context_manager.last_user_message
            ),

            "last_assistant_message": (
                context_manager.last_assistant_message
            ),

            "history": history,
        }

        # ==========================================
        # MEMORIA RELEVANTE
        # ==========================================

        context["memory"] = []

        if memory_manager is not None:

            try:
                relevant = memory_manager.get_relevant_memory(
                    context
                )

                if relevant:
                    context["memory"] = self._limit_memories(relevant)

            except AttributeError:
                # MemoryManager todavía no tiene
                # get_relevant_memory()
                context["memory"] = []

            except Exception as e:
                print(
                    f"[ContextBuilder] Error obteniendo memoria: {e}"
                )

        return context

    def _limit_memories(self, memories):
        """Recorta el contexto de memoria para reducir tokens y latencia."""
        if isinstance(memories, dict):
            memories = list(memories.values())
        if not isinstance(memories, (list, tuple)):
            return []
        return [str(memory)[:self.MAX_MEMORY_CHARS] for memory in memories[:self.MAX_MEMORIES]]
