import logging
from typing import Any, Dict, List, Optional, Tuple
from app.core.brain.brain_context import BrainContext

logger = logging.getLogger("BrainManager")


class BrainManager:
    """
    Capa de razonamiento y coordinación para SIRLUCAS AI.
    Analiza intenciones, planifica consultas a módulos de información
    y consolida contexto sin duplicar responsabilidades de almacenamiento.
    """

    def __init__(
        self,
        memory_manager: Any = None,
        knowledge_manager: Any = None,
        context_builder: Any = None,
        max_total_chars: int = 2000
    ) -> None:
        self.memory_manager = memory_manager
        self.knowledge_manager = knowledge_manager
        self.context_builder = context_builder
        self.max_total_chars = max_total_chars

    def process(
        self,
        message: str,
        conversation_history: Optional[Any] = None,
        parsed_intent: Optional[Dict[str, Any]] = None,
        action_result: Optional[Dict[str, Any]] = None
    ) -> BrainContext:
        """Punto de entrada principal para coordinar la recopilación de información."""
        logger.info("[BrainManager] Analizando mensaje e intención")
        
        plan = self._create_plan(message, parsed_intent, action_result)
        logger.info(
            f"[BrainManager] Plan generado: memory={plan['use_memory']} "
            f"knowledge={plan['use_knowledge']} context={plan['use_context']}"
        )

        raw_memory, raw_knowledge, context_data = self._fetch_data_safely(
            plan=plan,
            message=message,
            conversation_history=conversation_history,
            action_result=action_result
        )

        filtered_memory, filtered_knowledge, sources = self._filter_and_truncate(
            memory=raw_memory,
            knowledge=raw_knowledge
        )

        if action_result:
            sources.append("action_execution")

        return BrainContext(
            message=message,
            needs_memory=plan["use_memory"],
            needs_knowledge=plan["use_knowledge"],
            needs_context=plan["use_context"],
            memory_data=filtered_memory,
            knowledge_data=filtered_knowledge,
            recent_context=context_data,
            action_result=action_result,
            sources_used=sources
        )

    def _create_plan(
        self,
        message: str,
        parsed_intent: Optional[Dict[str, Any]] = None,
        action_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Determina de forma determinista qué fuentes de datos consultar."""
        msg_lower = message.lower()

        # Si hubo una acción determinista previa, reducir consultas
        if action_result or (parsed_intent and parsed_intent.get("is_command")):
            return {"use_memory": False, "use_knowledge": False, "use_context": True}

        memory_triggers = ["mi", "mis", "recuerdas", "proyecto", "dije", "tengo", "guardaste"]
        knowledge_triggers = ["qué es", "quién es", "cómo funciona", "python", "explicar", "definición", "saber sobre"]

        use_memory = any(trigger in msg_lower for trigger in memory_triggers)
        use_knowledge = any(trigger in msg_lower for trigger in knowledge_triggers)

        if not use_memory and not use_knowledge:
            use_memory = True
            use_context = True
        else:
            use_context = True

        return {
            "use_memory": use_memory,
            "use_knowledge": use_knowledge,
            "use_context": use_context
        }

    def _fetch_data_safely(
        self,
        plan: Dict[str, bool],
        message: str,
        conversation_history: Optional[Any],
        action_result: Optional[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """Recupera datos con aislamiento estricto de excepciones."""
        memory_res: List[Dict[str, Any]] = []
        knowledge_res: List[Dict[str, Any]] = []
        context_res: Dict[str, Any] = {}

        # 1. Recuperar Memoria
        if plan["use_memory"] and self.memory_manager:
            try:
                # Se envía una estructura dict compatible con MemoryManager y ContextBuilder
                mem_query = {"last_user_message": message, "topic": None} if isinstance(message, str) else message

                if hasattr(self.memory_manager, "get_relevant_memory"):
                    memories = self.memory_manager.get_relevant_memory(mem_query)
                elif hasattr(self.memory_manager, "search_memory"):
                    memories = self.memory_manager.search_memory(query=message)
                else:
                    memories = []
                
                memory_res = memories if isinstance(memories, list) else []
                logger.info(f"[BrainManager] Memorias recuperadas: {len(memory_res)}")
            except Exception as e:
                logger.error(f"[BrainManager] Error al recuperar memoria: {e}")
                memory_res = []

        # 2. Recuperar Conocimiento
        if plan["use_knowledge"] and self.knowledge_manager:
            try:
                if hasattr(self.knowledge_manager, "search"):
                    kn_data = self.knowledge_manager.search({"topic": message, "value": message})
                elif hasattr(self.knowledge_manager, "execute"):
                    kn_data = self.knowledge_manager.execute({"topic": message})
                else:
                    kn_data = []

                if isinstance(kn_data, list):
                    knowledge_res = kn_data
                elif kn_data:
                    knowledge_res = [{"source": "knowledge", "content": str(kn_data)}]
                logger.info(f"[BrainManager] Conocimiento recuperado: {len(knowledge_res)}")
            except Exception as e:
                logger.error(f"[BrainManager] Error al recuperar conocimiento: {e}")
                knowledge_res = []

        # 3. Construir Contexto
        if plan["use_context"] and self.context_builder:
            try:
                if hasattr(self.context_builder, "build"):
                    # Se llama a build() pasando el gestor/historial como primer argumento posicional
                    context_res = self.context_builder.build(conversation_history)
                else:
                    context_res = {"history": conversation_history or []}
                logger.info("[BrainManager] Contexto preparado correctamente")
            except Exception as e:
                logger.error(f"[BrainManager] Error al construir contexto: {e}")
                context_res = {}

        return memory_res, knowledge_res, context_res

    def _filter_and_truncate(
        self,
        memory: List[Any],
        knowledge: List[Any]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        """Deduplica información y trunca textos para mantener acotado el prompt."""
        cleaned_memory: List[Dict[str, Any]] = []
        cleaned_knowledge: List[Dict[str, Any]] = []
        sources: List[str] = []
        current_chars = 0

        # Normalizar y filtrar memorias
        for item in memory:
            content = item.get("content") if isinstance(item, dict) else str(item)
            if content and content not in [m["content"] for m in cleaned_memory]:
                if current_chars + len(content) <= self.max_total_chars:
                    cleaned_memory.append({"source": "memory", "content": content})
                    current_chars += len(content)

        if cleaned_memory:
            sources.append("memory_manager")

        # Normalizar y filtrar conocimiento
        for item in knowledge:
            content = item.get("content") if isinstance(item, dict) else str(item)
            if content and content not in [k["content"] for k in cleaned_knowledge]:
                if current_chars + len(content) <= self.max_total_chars:
                    cleaned_knowledge.append({"source": "knowledge", "content": content})
                    current_chars += len(content)

        if cleaned_knowledge:
            sources.append("knowledge_manager")

        return cleaned_memory, cleaned_knowledge, sources