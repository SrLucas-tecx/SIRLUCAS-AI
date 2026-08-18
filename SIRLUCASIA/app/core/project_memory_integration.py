"""
ProjectMemoryIntegration
=======================
Integra RuleEngine + ProjectMemoryHandler con ConversationManager
para auto-guardar proyectos de forma automática.

Punto de entrada: ConversationManager.process() 
   → RuleEngine.match(message)
   → ProjectMemoryHandler.handle_rule()
   → MemoryManager.remember_project()
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.rule_engine import RuleEngine
from app.core.memory_manager import MemoryManager
from app.modules.project_memory_handler import ProjectMemoryHandler

logger = logging.getLogger(__name__)


class ProjectMemoryIntegration:
    """
    Integración centralizada de RuleEngine + ProjectMemoryHandler.
    
    Responsabilidades:
    1. Cargar reglas desde JSON (parser_rules.json y parser_rules_proyectos.json)
    2. Crear RuleEngine con todas las reglas
    3. Ejecutar RuleEngine en cada mensaje
    4. Si hay coincidencia de proyecto, delegar a ProjectMemoryHandler
    5. Integrar resultados con ConversationManager
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Inicializa el sistema de integración.
        
        Args:
            memory_manager: Instancia de MemoryManager compartida
        """
        self.memory = memory_manager
        self.rule_engine = None
        self.project_handler = ProjectMemoryHandler(memory_manager)
        self.logger = logger
        
        # Cargar y compilar reglas
        self._load_and_compile_rules()
    
    def _load_and_compile_rules(self) -> None:
        """
        Carga todas las reglas desde JSON y crea el RuleEngine.
        """
        try:
            # Ruta base relativa a este archivo
            base_path = Path(__file__).parent.parent / "modules"
            
            rules = []
            
            # Cargar reglas principales
            rules_file = base_path / "parser_rules.json"
            if rules_file.exists():
                with open(rules_file, "r", encoding="utf-8") as f:
                    rules.extend(json.load(f))
                self.logger.info(
                    f"[ProjectMemoryIntegration] Cargadas {len(json.load(open(rules_file)))} reglas base"
                )
            
            # Cargar reglas específicas de proyectos
            project_rules_file = base_path / "parser_rules_proyectos.json"
            if project_rules_file.exists():
                with open(project_rules_file, "r", encoding="utf-8") as f:
                    project_rules = json.load(f)
                    rules.extend(project_rules)
                self.logger.info(
                    f"[ProjectMemoryIntegration] Cargadas {len(project_rules)} reglas de proyectos"
                )
            
            # Crear RuleEngine
            self.rule_engine = RuleEngine(rules)
            
            self.logger.info(
                f"[ProjectMemoryIntegration] RuleEngine compilado con {len(rules)} reglas totales"
            )
            
        except Exception as e:
            self.logger.error(
                f"[ProjectMemoryIntegration] Error cargando reglas: {e}"
            )
            self.rule_engine = RuleEngine([])
    
    def process_message(self, message: str) -> tuple[Any, Any]:
        """
        Procesa un mensaje y extrae acciones de proyecto si existen.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            (rule_result: dict o None, handler_result: ActionResult o None)
        """
        
        if not self.rule_engine or not message:
            return None, None
        
        try:
            # Ejecutar RuleEngine
            rule_result = self.rule_engine.match(message)
            
            if not rule_result:
                self.logger.debug(f"[ProjectMemoryIntegration] No coincidió ninguna regla para: {message}")
                return None, None
            
            self.logger.debug(
                f"[ProjectMemoryIntegration] Regla coincidida: {rule_result.get('rule')}"
            )
            
            # Si es una regla de proyecto, delegarla al handler
            if rule_result.get("module") == "memory" and "project" in rule_result.get("command", ""):
                handler_result = self.project_handler.handle_rule(rule_result)
                return rule_result, handler_result
            
            return rule_result, None
            
        except Exception as e:
            self.logger.error(
                f"[ProjectMemoryIntegration] Error procesando mensaje: {e}"
            )
            return None, None
    
    def auto_save_project(self, message: str) -> ActionResult | None:
        """
        Punto de entrada público: procesa mensaje y guarda proyecto si aplica.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            ActionResult si se guardó un proyecto, None si no aplica
        """
        
        rule_result, handler_result = self.process_message(message)
        
        if handler_result:
            self.logger.info(
                f"[ProjectMemoryIntegration] Proyecto auto-guardado: {handler_result.message}"
            )
            return handler_result
        
        return None
    
    def get_project_suggestions(self, message: str) -> list[str]:
        """
        Extrae sugerencias relacionadas con proyectos del mensaje.
        Útil para logging y debugging.
        
        Args:
            message: Mensaje del usuario
            
        Returns:
            Lista de sugerencias encontradas
        """
        
        suggestions = []
        
        project_keywords = [
            "proyecto", "trabajo", "desarrollo", "app", "aplicación",
            "sistema", "software", "programa", "herramienta"
        ]
        
        message_lower = message.lower()
        
        for keyword in project_keywords:
            if keyword in message_lower:
                suggestions.append(keyword)
        
        return suggestions

