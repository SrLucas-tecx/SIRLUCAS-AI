"""
ProjectMemoryHandler
====================
Integra la detección de proyectos (vía RuleEngine) con MemoryManager
para guardar automáticamente proyectos en memoria permanente.

Punto de integración: ConversationManager → ProjectMemoryHandler → MemoryManager
"""

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.memory_manager import MemoryManager
import logging

logger = logging.getLogger(__name__)


class ProjectMemoryHandler:
    """
    Maneja la detección y guardado automático de proyectos.
    
    Casos soportados:
    1. Usuario menciona: "mi proyecto es X" → remember_project(X)
    2. Usuario menciona: "trabajo en X que es Y" → remember_project(X, description=Y)
    3. Usuario pregunta: "cuál es mi proyecto" → recall_project()
    4. Usuario menciona: "cambio a proyecto X" → update_project(X)
    5. Usuario pregunta: "dame detalles del proyecto" → get_project_details()
    6. Usuario pregunta: "lista mis proyectos" → list_projects()
    """
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Inicializa el handler con acceso a MemoryManager.
        
        Args:
            memory_manager: Instancia de MemoryManager para guardar proyectos
        """
        self.memory = memory_manager
        self.logger = logger
    
    # ==========================================================
    # HANDLERS DE REGLAS (mapean RuleEngine results → memory)
    # ==========================================================
    
    def handle_rule(self, rule_result: dict) -> ActionResult:
        """
        Punto de entrada principal: recibe resultado de RuleEngine
        y ejecuta el handler correspondiente.
        
        Args:
            rule_result: Dict con {rule, module, command, ...fields...}
            
        Returns:
            ActionResult con éxito/error del guardado
        """
        
        if not rule_result or rule_result.get("module") != "memory":
            return None
        
        command = rule_result.get("command")
        
        handlers = {
            "remember_project": self.handle_remember_project,
            "remember_project_description": self.handle_remember_project_with_description,
            "recall_project": self.handle_recall_project,
            "update_project": self.handle_update_project,
            "get_project_details": self.handle_get_project_details,
            "list_projects": self.handle_list_projects,
            "search_project": self.handle_search_project,
            "forget_project": self.handle_forget_project,
            "create_project": self.handle_create_project,
            "add_project_detail": self.handle_add_project_detail,
        }
        
        handler = handlers.get(command)
        if handler:
            return handler(rule_result)
        
        return ActionResult(
            success=False,
            status=ActionStatus.ERROR,
            module="project_memory",
            message=f"Handler no encontrado para comando: {command}"
        )
    
    # ==========================================================
    # HANDLERS ESPECÍFICOS
    # ==========================================================
    
    def handle_remember_project(self, rule_result: dict) -> ActionResult:
        """
        Guarda un proyecto nuevo en memoria.
        Detecta: "mi proyecto es X", "trabajo en X"
        """
        project_name = rule_result.get("project_name")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó el nombre del proyecto."
            )
        
        result = self.memory.remember_project(
            project_name=project_name,
            description=""
        )
        
        self.logger.info(
            f"[ProjectMemoryHandler] Proyecto '{project_name}' guardado en memoria"
        )
        
        return result
    
    def handle_remember_project_with_description(self, rule_result: dict) -> ActionResult:
        """
        Guarda un proyecto con descripción en memoria.
        Detecta: "mi proyecto es X - descripción Y"
        """
        project_name = rule_result.get("project_name")
        description = rule_result.get("description", "")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó el nombre del proyecto."
            )
        
        result = self.memory.remember_project(
            project_name=project_name,
            description=description
        )
        
        self.logger.info(
            f"[ProjectMemoryHandler] Proyecto '{project_name}' guardado con descripción"
        )
        
        return result
    
    def handle_recall_project(self, rule_result: dict) -> ActionResult:
        """
        Recupera el proyecto actual de memoria.
        Detecta: "¿cuál es mi proyecto?"
        """
        
        # Busca memorias con categoría "projects" o alias "mi proyecto"
        projects = self.memory.find_by_category({"category": "projects", "limit": 1})
        
        if not projects or not projects.data:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="project_memory",
                message="No hay ningún proyecto guardado en memoria."
            )
        
        project_data = projects.data[0] if isinstance(projects.data, list) else projects.data
        project_name = project_data.get("name", "Desconocido")
        description = project_data.get("description", "")
        
        message = f"Tu proyecto actual es: {project_name}"
        if description:
            message += f"\nDescripción: {description}"
        
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="project_memory",
            message=message,
            data=project_data
        )
    
    def handle_update_project(self, rule_result: dict) -> ActionResult:
        """
        Actualiza el proyecto actual.
        Detecta: "cambio mi proyecto a X"
        """
        project_name = rule_result.get("project_name")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó el nuevo proyecto."
            )
        
        # Primero olvida proyectos anteriores
        self.memory.clear_category({"category": "projects"})
        
        # Luego guarda el nuevo
        result = self.memory.remember_project(
            project_name=project_name,
            description=""
        )
        
        self.logger.info(
            f"[ProjectMemoryHandler] Proyecto actualizado a '{project_name}'"
        )
        
        return result
    
    def handle_get_project_details(self, rule_result: dict) -> ActionResult:
        """
        Obtiene detalles del proyecto actual.
        Detecta: "dame detalles del proyecto"
        """
        
        projects = self.memory.find_by_category({"category": "projects", "limit": 1})
        
        if not projects or not projects.data:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="project_memory",
                message="No hay ningún proyecto guardado."
            )
        
        project_data = projects.data[0] if isinstance(projects.data, list) else projects.data
        
        details = f"""
        **Proyecto: {project_data.get('name', 'Desconocido')}**
        
        Descripción: {project_data.get('description', 'Sin descripción')}
        Importancia: {project_data.get('importance', 0)}
        Creado: {project_data.get('created_at', 'Desconocida')}
        Última modificación: {project_data.get('updated_at', 'Desconocida')}
        Veces consultado: {project_data.get('times_used', 0)}
        """
        
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="project_memory",
            message=details,
            data=project_data
        )
    
    def handle_list_projects(self, rule_result: dict) -> ActionResult:
        """
        Lista todos los proyectos guardados.
        Detecta: "lista mis proyectos"
        """
        
        projects = self.memory.find_by_category({"category": "projects", "limit": 100})
        
        if not projects or not projects.data:
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="project_memory",
                message="No hay proyectos guardados todavía.",
                data=[]
            )
        
        project_list = projects.data if isinstance(projects.data, list) else [projects.data]
        
        message = f"**Tienes {len(project_list)} proyecto(s) guardado(s):**\n\n"
        for i, proj in enumerate(project_list, 1):
            name = proj.get('name', 'Desconocido')
            desc = proj.get('description', 'Sin descripción')
            message += f"{i}. {name} - {desc}\n"
        
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="project_memory",
            message=message,
            data=project_list
        )
    
    def handle_search_project(self, rule_result: dict) -> ActionResult:
        """
        Busca un proyecto específico.
        Detecta: "busca el proyecto X"
        """
        project_name = rule_result.get("project_name")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó el proyecto a buscar."
            )
        
        project = self.memory.get_project(project_name)
        
        if not project:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="project_memory",
                message=f"No encontré un proyecto llamado '{project_name}'."
            )
        
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="project_memory",
            message=f"Encontré el proyecto: {project_name}\n{project}",
            data=project
        )
    
    def handle_forget_project(self, rule_result: dict) -> ActionResult:
        """
        Olvida un proyecto.
        Detecta: "olvida el proyecto X"
        """
        project_name = rule_result.get("project_name")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó qué proyecto olvidar."
            )
        
        key = f"project:{project_name.lower()}"
        
        result = self.memory.forget({
            "key": key
        })
        
        self.logger.info(
            f"[ProjectMemoryHandler] Proyecto '{project_name}' olvidado"
        )
        
        return result
    
    def handle_create_project(self, rule_result: dict) -> ActionResult:
        """
        Crea un nuevo proyecto.
        Detecta: "crea un proyecto llamado X"
        """
        project_name = rule_result.get("project_name")
        
        if not project_name:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó el nombre del proyecto."
            )
        
        return self.handle_remember_project(rule_result)
    
    def handle_add_project_detail(self, rule_result: dict) -> ActionResult:
        """
        Agrega un detalle al proyecto actual.
        Detecta: "agrega a mi proyecto X"
        """
        detail = rule_result.get("detail")
        
        if not detail:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="project_memory",
                message="No se especificó qué agregar al proyecto."
            )
        
        # Recupera proyecto actual
        projects = self.memory.find_by_category({"category": "projects", "limit": 1})
        
        if not projects or not projects.data:
            return ActionResult(
                success=False,
                status=ActionStatus.WARNING,
                module="project_memory",
                message="No hay proyecto actual para agregar detalles."
            )
        
        project_data = projects.data[0] if isinstance(projects.data, list) else projects.data
        current_desc = project_data.get("description", "")
        
        # Actualiza descripción
        new_desc = f"{current_desc}\n{detail}".strip()
        
        result = self.memory.update({
            "key": f"project:{project_data.get('name', '').lower()}",
            "value": {
                "name": project_data.get('name'),
                "description": new_desc
            }
        })
        
        self.logger.info(
            f"[ProjectMemoryHandler] Detalle agregado al proyecto"
        )
        
        return result