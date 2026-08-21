from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class BrainContext:
    """Estructura estandarizada de transporte de contexto procesado."""
    message: str
    needs_memory: bool = False
    needs_knowledge: bool = False
    needs_context: bool = False
    memory_data: List[Dict[str, Any]] = field(default_factory=list)
    knowledge_data: List[Dict[str, Any]] = field(default_factory=list)
    recent_context: Dict[str, Any] = field(default_factory=dict)
    action_result: Optional[Dict[str, Any]] = None
    sources_used: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "needs_memory": self.needs_memory,
            "needs_knowledge": self.needs_knowledge,
            "needs_context": self.needs_context,
            "memory_data": self.memory_data,
            "knowledge_data": self.knowledge_data,
            "recent_context": self.recent_context,
            "action_result": self.action_result,
            "sources_used": self.sources_used,
        }