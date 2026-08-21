class ContextBuilder:
    """
    Construye un contexto controlado para Ollama.

    - Usa ContextManager para contexto de corto plazo.
    - Limita el historial enviado al modelo.
    - Integra únicamente memoria relevante.
    - Limita la cantidad y tamaño de las memorias.
    """

    # ==========================================
    # CONFIGURACIÓN
    # ==========================================

    MAX_HISTORY = 4
    MAX_MEMORIES = 5
    MAX_MEMORY_CHARS = 500

    # ==========================================
    # CONSTRUCCIÓN DEL CONTEXTO
    # ==========================================

    def build(self, context_manager, memory_manager=None):
        """
        Construye el contexto que posteriormente será enviado
        al PromptManager y a Ollama.
        """

        if context_manager is None:
            return {}

        # ==========================================
        # HISTORIAL DE CONVERSACIÓN
        # ==========================================

        history = self._safe_call(
            context_manager,
            "conversation",
            default=[]
        )

        if not isinstance(history, list):
            history = []

        # Solo conservar los últimos turnos
        history = history[-self.MAX_HISTORY:]

        # ==========================================
        # CONTEXTO PRINCIPAL
        # ==========================================

        context = {
            "topic": self._safe_call(
                context_manager,
                "topic"
            ),

            "module": self._safe_call(
                context_manager,
                "module"
            ),

            "command": self._safe_call(
                context_manager,
                "command"
            ),

            "program": self._safe_call(
                context_manager,
                "program"
            ),

            "document": self._safe_call(
                context_manager,
                "document"
            ),

            "search": self._safe_call(
                context_manager,
                "search"
            ),

            "task": self._safe_call(
                context_manager,
                "task"
            ),

            "goal": self._safe_call(
                context_manager,
                "goal"
            ),

            "conversation_mode": self._safe_call(
                context_manager,
                "conversation_mode"
            ),

            "last_user_message": self._safe_call(
                context_manager,
                "last_user_message"
            ),

            "last_assistant_message": self._safe_call(
                context_manager,
                "last_assistant_message"
            ),

            "history": history,

            # Se llena más abajo
            "memory": [],
        }

        # ==========================================
        # MEMORIA RELEVANTE
        # ==========================================

        if memory_manager is not None:

            get_relevant_memory = getattr(
                memory_manager,
                "get_relevant_memory",
                None
            )

            if not callable(get_relevant_memory):

                print(
                    "[ContextBuilder] MemoryManager no tiene "
                    "get_relevant_memory()."
                )

            else:

                try:

                    relevant = get_relevant_memory({
                        "last_user_message": (
                            context["last_user_message"]
                        ),
                        "topic": context["topic"],
                    })

                    if relevant:

                        context["memory"] = (
                            self._limit_memories(
                                relevant
                            )
                        )

                except Exception as e:

                    print(
                        "[ContextBuilder] Error obteniendo "
                        f"memoria: {e}"
                    )

        return context

    # ==========================================
    # LIMITAR MEMORIAS
    # ==========================================

    def _limit_memories(self, memories):
        """
        Reduce la cantidad y tamaño de las memorias
        antes de enviarlas a Ollama.
        """

        if isinstance(memories, dict):
            memories = list(memories.values())

        if not isinstance(
            memories,
            (list, tuple)
        ):
            return []

        limited_memories = []

        for memory in memories[:self.MAX_MEMORIES]:

            formatted_memory = (
                self._format_memory(memory)
            )

            if formatted_memory:

                limited_memories.append(
                    formatted_memory[
                        :self.MAX_MEMORY_CHARS
                    ]
                )

        return limited_memories

    # ==========================================
    # FORMATEAR MEMORIA
    # ==========================================

    def _format_memory(self, memory):
        """
        Convierte una memoria a un formato compacto
        y fácil de entender para Ollama.
        """

        # ------------------------------------------
        # SI YA ES TEXTO
        # ------------------------------------------

        if isinstance(memory, str):
            return memory.strip()

        # ------------------------------------------
        # SI ES DICCIONARIO
        # ------------------------------------------

        if isinstance(memory, dict):

            key = (
                memory.get("key")
                or memory.get("name")
                or memory.get("memory_key")
            )

            value = memory.get("value")

            category = memory.get(
                "category"
            )

            # --------------------------------------
            # VALUE SIMPLE
            # --------------------------------------

            if isinstance(
                value,
                (str, int, float, bool)
            ):

                if key:

                    if category:

                        return (
                            f"{key}: {value} "
                            f"(categoría: {category})"
                        )

                    return f"{key}: {value}"

                return str(value)

            # --------------------------------------
            # VALUE COMO DICCIONARIO
            # --------------------------------------

            if isinstance(value, dict):

                name = value.get("name")

                description = value.get(
                    "description"
                )

                parts = []

                if key:
                    parts.append(
                        str(key)
                    )

                if name:
                    parts.append(
                        f"nombre: {name}"
                    )

                if description:
                    parts.append(
                        f"descripción: {description}"
                    )

                if category:
                    parts.append(
                        f"categoría: {category}"
                    )

                if parts:
                    return " | ".join(parts)

            # --------------------------------------
            # VALUE COMO LISTA
            # --------------------------------------

            if isinstance(value, list):

                value_text = ", ".join(
                    str(item)
                    for item in value
                )

                if key:
                    return (
                        f"{key}: {value_text}"
                    )

                return value_text

            # --------------------------------------
            # FALLBACK
            # --------------------------------------

            if key and value is not None:
                return f"{key}: {value}"

            return ""

        # ------------------------------------------
        # CUALQUIER OTRO TIPO
        # ------------------------------------------

        return str(memory)

    # ==========================================
    # LLAMADA SEGURA A CONTEXTMANAGER O DICT
    # ==========================================

    def _safe_call(
        self,
        obj,
        key,
        default=None
    ):
        """
        Obtiene un valor de obj de forma segura, ya sea invocando
        un método, leyendo un atributo o buscando una clave de diccionario.
        """
        if obj is None:
            return default

        # 1. Si obj es un diccionario
        if isinstance(obj, dict):
            val = obj.get(key)
            return val if val is not None else default

        # 2. Si obj es un objeto (ContextManager)
        attr = getattr(obj, key, None)

        if callable(attr):
            try:
                result = attr()
                return result if result is not None else default
            except Exception as e:
                print(f"[ContextBuilder] Error en {key}(): {e}")
                return default

        elif attr is not None:
            return attr

        return default