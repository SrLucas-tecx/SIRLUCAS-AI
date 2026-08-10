import re
from collections import deque
from datetime import datetime

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.context_stack import ContextStack

# ==================================================
# ContextManager
# Memoria de CORTO PLAZO de SIRLUCAS AI.
#
# Guarda únicamente el contexto de la conversación actual:
# de qué se está hablando, qué módulo/comando se ejecutó,
# qué programa/documento/archivo/persona está "activo",
# qué se dijo en los últimos turnos y qué variables
# temporales se definieron durante la charla.
#
# NO es memoria permanente: para eso existe MemoryManager.
# ContextManager se reinicia con clear()/reset() y no
# persiste nada por sí mismo salvo que otro componente
# (JSONManager, HistoryManager) decida serializarlo con
# to_dict()/from_dict().
#
# Este componente está pensado para integrarse con:
#   - Router          -> decide el módulo/comando siguiente
#                         usando el contexto (p.ej. resolver "ciérralo")
#   - ActionPlanner    -> arma acciones usando current_* y pending_actions
#   - RuleEngine       -> puede leer conversation_mode, current_topic, etc.
#   - Logger           -> recibe los mensajes de depuración
#   - Un futuro LLM (Ollama) -> puede recibir to_dict() como "memoria
#                         de trabajo" para dar respuestas coherentes
#                         con el hilo de la conversación.
# ==================================================

MAX_HISTORY_TURNS = 20
MAX_RECENT_ITEMS = 10

# Palabras clave que permiten identificar a qué tipo de contexto
# se refiere una referencia lingüística ("ese archivo", "la aplicación"...)
PRONOUN_KEYWORDS = {
    "programa": "program",
    "aplicacion": "program",
    "aplicación": "program",
    "app": "program",
    "documento": "document",
    "archivo": "file",
    "archivos": "file",
    "carpeta": "folder",
    "carpetas": "folder",
    "directorio": "folder",
    "url": "url",
    "enlace": "url",
    "pagina": "url",
    "página": "url",
    "busqueda": "search",
    "búsqueda": "search",
    "persona": "person",
    "contacto": "person",
    "tarea": "task",
    "entidad": "entity",
}

# Pronombres/referencias genéricas sin palabra clave asociada.
# Se resuelven usando la última entidad "tocada" en cualquier pila.
GENERIC_PRONOUNS = ("lo", "la", "los", "las", "eso", "esto", "esa", "ese", "esos", "esas")


class ContextManager:
    """
    Memoria de corto plazo del asistente SIRLUCAS AI.

    Mantiene el estado de la conversación actual (tema, módulo,
    comando, entidades activas, historial corto, variables
    temporales) y delega el almacenamiento apilado por categoría
    en un ContextStack.
    """

    # ==========================================
    # Construcción
    # ==========================================
    def __init__(self, logger=None, max_history: int = MAX_HISTORY_TURNS,
                 max_stack_size: int = MAX_RECENT_ITEMS):
        self.logger = logger
        self.max_history = max_history
        self.stack = ContextStack(max_size=max_stack_size)
        self.clear()

    # ==========================================
    # Reinicio TOTAL
    # Borra pilas, historial, variables y entidades.
    # Se usa al iniciar una conversación nueva.
    # ==========================================
    def clear(self):
        self.turn_number = 0

        # ---- Tema / clasificación ----
        self.current_topic = None
        self.main_topic = None
        self.sub_topic = None

        # ---- Enrutamiento ----
        self.current_module = None
        self.current_command = None

        # ---- Entidades activas ----
        self.current_program = None
        self.current_document = None
        self.current_search = None
        self.current_person = None
        self.current_entity = None
        self.current_file = None
        self.current_folder = None
        self.current_url = None
        self.current_task = None
        self.current_goal = None

        # ---- Ejecución ----
        self.current_action = None
        self.current_answer = None
        self.last_result = None

        # ---- Conversación ----
        self.conversation_mode = "default"
        self.last_user_message = None
        self.last_assistant_message = None

        # ---- Memoria de trabajo ----
        self.pending_actions = []
        self.working_memory = {}
        self.conversation_entities = {}
        self.conversation_variables = {}

        # ---- Recientes (para heurísticas rápidas) ----
        self.recent_topics = deque(maxlen=MAX_RECENT_ITEMS)
        self.recent_modules = deque(maxlen=MAX_RECENT_ITEMS)
        self.recent_commands = deque(maxlen=MAX_RECENT_ITEMS)

        # ---- Historial corto (últimos 20 turnos) ----
        self.history = deque(maxlen=self.max_history)

        # ---- Timestamps ----
        self.timestamps = {
            "created_at": datetime.now().isoformat(),
            "last_update": None,
        }

        # Última entidad "tocada" en cualquier pila (para resolver
        # pronombres genéricos como "lo"/"la" sin palabra clave)
        self._last_touched = None

        self.stack.clear()
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="clear",
            message="Contexto limpiado."
        )
    

    # ==========================================
    # Reinicio PARCIAL (suave)
    # Limpia solo lo relativo a la "tarea en curso"
    # (acción/objetivo/tarea/resultados pendientes),
    # sin perder pilas, historial ni variables.
    # Útil al terminar una tarea puntual dentro de
    # la misma conversación.
    # ==========================================
    def reset(self):
        self.current_task = None
        self.current_goal = None
        self.current_action = None
        self.current_answer = None
        self.pending_actions = []
        self.working_memory = {}

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="reset",
            message="Contexto reiniciado."
        )   

    # ==========================================
    # Actualizar contexto con el resultado de un turno
    # ==========================================
    def update(self, data: dict):
        """
        Actualiza el contexto con la información de un nuevo turno.

        `data` puede incluir cualquiera de estas claves (todas opcionales):
            topic, main_topic, sub_topic, module, command,
            program, document, search, entity, person, file,
            folder, url, task, goal, action, answer, result,
            user_message, assistant_message, conversation_mode
        """
        data = data or {}
        self.turn_number += 1
        now = datetime.now().isoformat()

        topic = data.get("topic")
        module = data.get("module")
        command = data.get("command")

        # El pipeline entrega el mensaje del usuario como `raw_message`
        # (o `normalized`), así que se aceptan como origen alternativo.
        user_message = (
            data.get("user_message")
            or data.get("raw_message")
            or data.get("normalized")
        )
        assistant_message = (
            data.get("assistant_message")
            or data.get("answer")
        )

        # ---- Tema ----
        if topic:
            self.current_topic = topic
            self.recent_topics.append(topic)
        if data.get("main_topic"):
            self.main_topic = data["main_topic"]
        if data.get("sub_topic"):
            self.sub_topic = data["sub_topic"]

        # ---- Enrutamiento ----
        if module:
            self.current_module = module
            self.recent_modules.append(module)
        if command:
            self.current_command = command
            self.recent_commands.append(command)
        if data.get("conversation_mode"):
            self.conversation_mode = data["conversation_mode"]

        # ---- Compatibilidad con el comportamiento original:
        #      si no llega una entidad explícita, se infiere del
        #      módulo + topic, igual que la versión anterior. ----
        if module == "system" and topic and not data.get("program"):
            self.push_program(topic)
        elif module == "document" and topic and not data.get("document"):
            self.push_document(topic)
        elif module in ("knowledge", "web") and topic and not data.get("search"):
            self.push_search(topic)

        # ---- Entidades explícitas ----
        if data.get("program"):
            self.push_program(data["program"])
        if data.get("document"):
            self.push_document(data["document"])
        if data.get("search"):
            self.push_search(data["search"])
        if data.get("entity"):
            self.remember_entity(data["entity"])
        if data.get("person"):
            self.push_person(data["person"])
        if data.get("file"):
            self.push_file(data["file"])
        if data.get("folder"):
            self.push_folder(data["folder"])
        if data.get("url"):
            self.push_url(data["url"])
        if data.get("task"):
            self.push_task(data["task"])
        if data.get("goal"):
            self.push_goal(data["goal"])

        # ---- Ejecución ----
        if data.get("action"):
            self.current_action = data["action"]
        if data.get("answer") is not None:
            self.current_answer = data["answer"]
            self.last_assistant_message = data["answer"]
        if data.get("result") is not None:
            self.last_result = data["result"]

        # ---- Mensajes ----
        if user_message is not None:
            self.last_user_message = user_message
        if assistant_message is not None:
            self.last_assistant_message = assistant_message

        # ---- Historial corto ----
        self.history.append({
            "usuario": user_message,
            "respuesta": assistant_message,
            "modulo": module,
            "comando": command,
            "tema": topic,
            "timestamp": now,
        })

        self.timestamps["last_update"] = now

        self._log_debug()
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="update",
            message="Contexto actualizado.",
            data={"turn_number": self.turn_number}
        )

    # ==========================================
    # Respuesta del asistente del turno actual
    # ==========================================
    def set_answer(self, answer):
        """
        Registra la respuesta del asistente para el turno ya abierto por
        `update()`, sin abrir un turno nuevo.
        """
        if answer is None:
            return

        self.current_answer = answer
        self.last_assistant_message = answer

        if self.history:
            self.history[-1]["respuesta"] = answer

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="set_answer",
            message="Respuesta registrada.",
            data={"turn_number": self.turn_number}
        )

    # ==========================================
    # Getters simples
    # ==========================================
    def turn(self):
        return self.turn_number

    def topic(self):
        return self.current_topic

    def module(self):
        return self.current_module

    def command(self):
        return self.current_command

    def program(self):
        return self.current_program

    def document(self):
        return self.current_document

    def search(self):
        return self.current_search

    def entity(self):
        return self.current_entity

    def person(self):
        return self.current_person

    def file(self):
        return self.current_file

    def folder(self):
        return self.current_folder

    def url(self):
        return self.current_url

    def task(self):
        return self.current_task

    def goal(self):
        return self.current_goal

    def answer(self):
        return self.current_answer

    def last_result(self):
        return self.last_result

    def conversation(self):
        """Devuelve el historial corto (últimos `max_history` turnos)."""
        return list(self.history)

    # ==========================================
    # PUSH -> delega en ContextStack y además
    # actualiza el puntero "current_*" y registra
    # cuál fue la última entidad tocada (para
    # resolve_reference).
    # ==========================================
    def push_program(self, value):
        self.stack.push_program(value)
        self.current_program = value
        self._touch("program", value)
        return value

    def push_document(self, value):
        self.stack.push_document(value)
        self.current_document = value
        self._touch("document", value)
        return value

    def push_search(self, value):
        self.stack.push_search(value)
        self.current_search = value
        self._touch("search", value)
        return value

    def push_entity(self, value):
        self.stack.push_entity(value)
        self.current_entity = value
        self._touch("entity", value)
        return value

    def push_person(self, value):
        self.stack.push_person(value)
        self.current_person = value
        self._touch("person", value)
        return value

    def push_file(self, value):
        self.stack.push_file(value)
        self.current_file = value
        self._touch("file", value)
        return value

    def push_folder(self, value):
        self.stack.push_folder(value)
        self.current_folder = value
        self._touch("folder", value)
        return value

    def push_url(self, value):
        self.stack.push_url(value)
        self.current_url = value
        self._touch("url", value)
        return value

    def push_task(self, value):
        self.stack.push_task(value)
        self.current_task = value
        self._touch("task", value)
        return value

    def push_goal(self, value):
        """
        El objetivo actual no tiene una pila dedicada en ContextStack
        (no fue solicitada); se administra únicamente como puntero
        "current_goal" dentro del ContextManager.
        """
        self.current_goal = value
        self._touch("goal", value)
        return value

    # ==========================================
    # POP -> saca el tope de la pila y realinea
    # el puntero "current_*" con el nuevo tope.
    # ==========================================
    def pop_program(self):
        value = self.stack.pop_program()
        self.current_program = self.stack.peek_program()
        return value

    def pop_document(self):
        value = self.stack.pop_document()
        self.current_document = self.stack.peek_document()
        return value

    def pop_search(self):
        value = self.stack.pop_search()
        self.current_search = self.stack.peek_search()
        return value

    def pop_entity(self):
        value = self.stack.pop_entity()
        self.current_entity = self.stack.peek_entity()
        return value

    def pop_person(self):
        value = self.stack.pop_person()
        self.current_person = self.stack.peek_person()
        return value

    def pop_file(self):
        value = self.stack.pop_file()
        self.current_file = self.stack.peek_file()
        return value

    def pop_folder(self):
        value = self.stack.pop_folder()
        self.current_folder = self.stack.peek_folder()
        return value

    def pop_url(self):
        value = self.stack.pop_url()
        self.current_url = self.stack.peek_url()
        return value

    def pop_task(self):
        value = self.stack.pop_task()
        self.current_task = self.stack.peek_task()
        return value

    # ==========================================
    # PEEK -> consulta el tope sin modificarlo
    # ==========================================
    def peek_program(self):
        return self.stack.peek_program()

    def peek_document(self):
        return self.stack.peek_document()

    def peek_search(self):
        return self.stack.peek_search()

    def peek_entity(self):
        return self.stack.peek_entity()

    def peek_person(self):
        return self.stack.peek_person()

    def peek_file(self):
        return self.stack.peek_file()

    def peek_folder(self):
        return self.stack.peek_folder()

    def peek_url(self):
        return self.stack.peek_url()

    def peek_task(self):
        return self.stack.peek_task()

    # ==========================================
    # Variables temporales de conversación
    # (namespace separado de working_memory)
    # ==========================================
    def set_variable(self, name: str, value):
        self.conversation_variables[name] = value
        return value

    def get_variable(self, name: str, default=None):
        return self.conversation_variables.get(name, default)

    def remove_variable(self, name: str):
        return self.conversation_variables.pop(name, None)

    def clear_variables(self):
        self.conversation_variables.clear()

    # ==========================================
    # Entidades genéricas de la conversación
    # ==========================================
    def remember_entity(self, entity):
        """
        Registra una entidad mencionada en la conversación.

        Acepta:
            - str: valor simple ("reporte.docx").
            - dict: {"type": "file"|"program"|"document"|"person"|
                     "folder"|"url"|"task"|"search"|"entity",
                     "value": <valor>}
              En este caso, además de guardarla en
              conversation_entities, se enruta automáticamente a la
              pila especializada correspondiente.
        """
        if entity is None:
            return None

        if isinstance(entity, dict):
            value = entity.get("value")
            etype = entity.get("type", "entity")
        else:
            value = entity
            etype = "entity"

        if value is None:
            return None

        self.conversation_entities[value] = {
            "type": etype,
            "value": value,
            "turn": self.turn_number,
            "timestamp": datetime.now().isoformat(),
        }

        route = {
            "program": self.push_program,
            "document": self.push_document,
            "search": self.push_search,
            "person": self.push_person,
            "file": self.push_file,
            "folder": self.push_folder,
            "url": self.push_url,
            "task": self.push_task,
        }

        if etype in route:
            route[etype](value)
        else:
            self.push_entity(value)

        return value

    def last_entities(self, limit: int = 5):
        """Devuelve las últimas entidades recordadas, más recientes primero."""
        items = sorted(
            self.conversation_entities.values(),
            key=lambda e: e["turn"],
            reverse=True,
        )
        return items[:limit]

    # ==========================================
    # Resolución de referencias / pronombres
    # ==========================================
    def _touch(self, ctx_type: str, value):
        """Registra cuál fue la última entidad tocada en cualquier pila."""
        self._last_touched = {
            "type": ctx_type,
            "value": value,
            "timestamp": datetime.now().isoformat(),
        }

    def resolve_reference(self, reference: str):
        """
        Resuelve una referencia lingüística al valor de contexto
        más probable al que apunta.

        Soporta:
            - Pronombres fusionados con el verbo: "ábrelo", "ciérralo",
              "elimínalo", "agrégalo", "renómbralo".
            - Pronombres sueltos: "lo", "la", "eso", "esto".
            - Frases demostrativas con palabra clave: "ese archivo",
              "esa carpeta", "ese documento", "el programa",
              "la aplicación".

        Estrategia:
            1. Si la referencia contiene una palabra clave conocida
               (archivo, carpeta, programa, etc.) se devuelve el tope
               de esa pila específica.
            2. Si no hay palabra clave, se devuelve la última entidad
               "tocada" (push_*) en cualquier pila, sea cual sea su tipo
               (comportamiento equivalente a "lo"/"la" genéricos).

        Devuelve:
            {"type": <tipo>, "value": <valor>} o None si no hay nada
            que resolver todavía.
        """
        if not reference:
            return None

        normalized = reference.strip().lower()

        getters = {
            "program": self.peek_program,
            "document": self.peek_document,
            "search": self.peek_search,
            "entity": self.peek_entity,
            "person": self.peek_person,
            "file": self.peek_file,
            "folder": self.peek_folder,
            "url": self.peek_url,
            "task": self.peek_task,
            "goal": lambda: self.current_goal,
        }

        # 1) Palabra clave explícita dentro de la referencia
        for keyword, ctx_type in PRONOUN_KEYWORDS.items():
            if keyword in normalized:
                value = getters.get(ctx_type, lambda: None)()
                if value:
                    return {"type": ctx_type, "value": value}

        # 2) Pronombre genérico -> última entidad tocada
        if self._last_touched:
            ctx_type = self._last_touched["type"]
            value = getters.get(ctx_type, lambda: self._last_touched["value"])()
            return {"type": ctx_type, "value": value or self._last_touched["value"]}

        return None

    def resolve_pronouns(self):
        """
        Analiza el último mensaje del usuario (last_user_message) en
        busca de pronombres/referencias implícitas y devuelve un
        diccionario {pronombre: {"type":..., "value":...}} con todo
        lo que pudo resolverse.

        Pensado para integrarse con un LLM: antes de reenviar el
        mensaje del usuario, el asistente puede "aclarar" a qué se
        refieren sus pronombres usando este método.
        """
        if not self.last_user_message:
            return {}

        text = self.last_user_message.strip().lower()
        resolved = {}

        for pronoun in GENERIC_PRONOUNS:
            # Coincide como palabra suelta ("ábrelo la") o pronombre
            # fusionado al final del verbo ("ciérralo")
            if re.search(rf"\b{pronoun}\b", text) or text.endswith(pronoun):
                result = self.resolve_reference(pronoun)
                if result:
                    resolved[pronoun] = result

        return resolved

    # ==========================================
    # Estadísticas
    # ==========================================
    def statistics(self):
        status = {
            "turn_number": self.turn_number,
            "current_topic": self.current_topic,
            "current_module": self.current_module,
            "current_command": self.current_command,
            "active_program": self.current_program,
            "active_document": self.current_document,
            "active_file": self.current_file,
            "active_folder": self.current_folder,
            "active_person": self.current_person,
            "active_entities": len(self.conversation_entities),
            "last_action": self.current_action,
            "last_result": self.last_result,
            "history_length": len(self.history),
            "variables_count": len(self.conversation_variables),
            "pending_actions": len(self.pending_actions),
            "stack": self.stack.statistics(),
        }
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="statistics",
            message="Estadísticas del contexto.",
            data=status
        )

    # ==========================================
    # Serialización (para JSONManager / HistoryManager
    # o para pasarle "memoria de trabajo" a un LLM)
    # ==========================================
    def to_dict(self):
        return {
            "turn_number": self.turn_number,
            "current_topic": self.current_topic,
            "main_topic": self.main_topic,
            "sub_topic": self.sub_topic,
            "current_module": self.current_module,
            "current_command": self.current_command,
            "current_program": self.current_program,
            "current_document": self.current_document,
            "current_search": self.current_search,
            "current_person": self.current_person,
            "current_entity": self.current_entity,
            "current_file": self.current_file,
            "current_folder": self.current_folder,
            "current_url": self.current_url,
            "current_task": self.current_task,
            "current_goal": self.current_goal,
            "current_action": self.current_action,
            "current_answer": self.current_answer,
            "conversation_mode": self.conversation_mode,
            "last_user_message": self.last_user_message,
            "last_assistant_message": self.last_assistant_message,
            "last_result": self.last_result,
            "pending_actions": list(self.pending_actions),
            "working_memory": dict(self.working_memory),
            "conversation_entities": dict(self.conversation_entities),
            "conversation_variables": dict(self.conversation_variables),
            "recent_topics": list(self.recent_topics),
            "recent_modules": list(self.recent_modules),
            "recent_commands": list(self.recent_commands),
            "timestamps": dict(self.timestamps),
            "history": list(self.history),
            "stack": self.stack.to_dict(),
        }

    def from_dict(self, data: dict):
        """Reconstruye el contexto completo a partir de to_dict()."""
        if not data:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="context",
                command="from_dict",
                message="Datos inválidos para reconstruir el contexto."
            )

        self.turn_number = data.get("turn_number", 0)
        self.current_topic = data.get("current_topic")
        self.main_topic = data.get("main_topic")
        self.sub_topic = data.get("sub_topic")
        self.current_module = data.get("current_module")
        self.current_command = data.get("current_command")
        self.current_program = data.get("current_program")
        self.current_document = data.get("current_document")
        self.current_search = data.get("current_search")
        self.current_person = data.get("current_person")
        self.current_entity = data.get("current_entity")
        self.current_file = data.get("current_file")
        self.current_folder = data.get("current_folder")
        self.current_url = data.get("current_url")
        self.current_task = data.get("current_task")
        self.current_goal = data.get("current_goal")
        self.current_action = data.get("current_action")
        self.current_answer = data.get("current_answer")
        self.conversation_mode = data.get("conversation_mode", "default")
        self.last_user_message = data.get("last_user_message")
        self.last_assistant_message = data.get("last_assistant_message")
        self.last_result = data.get("last_result")
        self.pending_actions = list(data.get("pending_actions", []))
        self.working_memory = dict(data.get("working_memory", {}))
        self.conversation_entities = dict(data.get("conversation_entities", {}))
        self.conversation_variables = dict(data.get("conversation_variables", {}))
        self.recent_topics = deque(data.get("recent_topics", []), maxlen=MAX_RECENT_ITEMS)
        self.recent_modules = deque(data.get("recent_modules", []), maxlen=MAX_RECENT_ITEMS)
        self.recent_commands = deque(data.get("recent_commands", []), maxlen=MAX_RECENT_ITEMS)
        self.timestamps = dict(data.get("timestamps", {}))
        self.history = deque(data.get("history", []), maxlen=self.max_history)

        self.stack.from_dict(data.get("stack", {}))
        self.sync()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="from_dict",
            message="Contexto reconstruido desde diccionario."
        )

    def sync(self):
        """
        Realinea los punteros "current_*" con el tope real de cada
        pila del ContextStack. Útil después de from_dict(), o si
        algún componente externo manipuló el ContextStack directamente.
        """
        self.current_program = self.stack.peek_program()
        self.current_document = self.stack.peek_document()
        self.current_search = self.stack.peek_search()
        self.current_entity = self.stack.peek_entity()
        self.current_person = self.stack.peek_person()
        self.current_file = self.stack.peek_file()
        self.current_folder = self.stack.peek_folder()
        self.current_url = self.stack.peek_url()
        self.current_task = self.stack.peek_task()

        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="sync",
            message="Contexto sincronizado.",
            data=self.to_dict()
        )


    # ==========================================
    # Utilidades auxiliares (no exigidas por la
    # especificación, pero coherentes con ella)
    # ==========================================
    def add_pending_action(self, action):
        """Encola una acción planificada (ActionPlanner) pendiente de ejecutar."""
        self.pending_actions.append(action)
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="add_pending_action",
            message="Acción pendiente agregada.",
            data={"action": action}
        )

    def pop_pending_action(self):
        """Saca y devuelve la siguiente acción pendiente (FIFO)."""
        if not self.pending_actions:
            return None
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="context",
            command="pop_pending_action",
            message="Acción pendiente sacada.",
            data={"action": self.pending_actions.pop(0)}
        )

    def set_working(self, key, value):
        """Guarda un dato efímero de trabajo (distinto de las variables de usuario)."""
        self.working_memory[key] = value
        return value

    def get_working(self, key, default=None):
        return self.working_memory.get(key, default)

    # ==========================================
    # Debug
    # ==========================================
    def _log_debug(self):
        lines = [
            "\n========== CONTEXT MANAGER ==========",
            f"Turno       : {self.turn_number}",
            f"Tema        : {self.current_topic}",
            f"Módulo      : {self.current_module}",
            f"Comando     : {self.current_command}",
            f"Programa    : {self.current_program}",
            f"Documento   : {self.current_document}",
            f"Búsqueda    : {self.current_search}",
            f"Archivo     : {self.current_file}",
            f"Carpeta     : {self.current_folder}",
            f"URL         : {self.current_url}",
            f"Persona     : {self.current_person}",
            f"Tarea       : {self.current_task}",
            "======================================\n",
        ]
        message = "\n".join(lines)

        if self.logger:
            try:
                self.logger.debug(message)
                return
            except AttributeError:
                pass

        print(message)

    def __repr__(self):
        return (
            f"<ContextManager turno={self.turn_number} "
            f"tema={self.current_topic!r} modulo={self.current_module!r}>"
        )