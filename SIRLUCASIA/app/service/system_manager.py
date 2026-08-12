"""
SystemManager
=============

Manager de dominio responsable de abrir, cerrar, reiniciar y consultar
el estado de aplicaciones del sistema operativo para SIRLUCAS AI.

LIMITACIÓN CONOCIDA (intencional): este módulo depende de comandos
exclusivos de Windows (`taskkill`, `tasklist`) y de resolución de
ejecutables al estilo Windows. El proyecto es Windows-only por
decisión de arquitectura; no tiene ni debe tener manejo multiplataforma.

DISEÑO: el registro de procesos abiertos por el asistente vive en
`ProcessRegistry`, una clase auxiliar separada y thread-safe (protegida
por `threading.RLock`), para que `SystemManager` no tenga que conocer
detalles de sincronización ni de la estructura de datos interna.
"""

from __future__ import annotations
import os
import logging
import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.database.program_database import ProgramDatabase

logger = logging.getLogger(__name__)

# Segundos que se espera confirmación de un subprocess (terminate/kill,
# o una llamada a taskkill/tasklist) antes de darlo por fallido/colgado.
SUBPROCESS_TIMEOUT_SECONDS = 5


class SystemCommand(StrEnum):
    """
    Comandos de dominio que SystemManager acepta vía `execute()`.

    `exists()` e `is_open()` son métodos públicos válidos y se pueden
    llamar directamente, pero NO se despachan vía `execute()`: su firma
    es `(self, app: str)`, incompatible con el contrato
    `method(data: dict)` que usa el dispatcher. Antes de esta versión,
    enviar `{"command": "is_open", ...}` a `execute()` producía un
    `AttributeError` no controlado (se pasaba el `dict` completo como
    si fuera el string `app`).
    """
    OPEN = "open"
    CLOSE = "close"
    RESTART = "restart"
    IS_OPEN = "is_open"
    


@dataclass(slots=True)
class TrackedProcess:
    """Un proceso abierto por SIRLUCAS AI, con metadata para diagnóstico."""

    popen: subprocess.Popen
    app_alias: str
    opened_at: datetime = field(default_factory=datetime.now)

    @property
    def pid(self) -> int:
        return self.popen.pid

    def is_alive(self) -> bool:
        # poll() consulta el handle específico del proceso que Popen
        # mantiene internamente, no el número de PID crudo — por eso
        # este diseño es inmune a la reutilización de PIDs por parte
        # de Windows tras la terminación del proceso original.
        return self.popen.poll() is None


class ProcessRegistry:
    """
    Registro thread-safe de los procesos que el propio SystemManager
    abrió, agrupados por nombre de ejecutable.

    Toda mutación pasa por `self._lock`, evitando condiciones de
    carrera si `open()`/`close()` llegan a invocarse desde hilos
    distintos en el futuro.
    """

    def __init__(self) -> None:
        self._by_program: dict[str, list[TrackedProcess]] = {}
        self._lock = threading.RLock()

    def track(self, program: str, popen: subprocess.Popen, app_alias: str) -> None:
        """Registra un proceso recién abierto. Nunca sobrescribe instancias previas."""
        with self._lock:
            self._by_program.setdefault(program, []).append(
                TrackedProcess(popen=popen, app_alias=app_alias)
            )

    def alive_for(self, program: str) -> list[TrackedProcess]:
        """
        Devuelve los procesos vivos de `program`, purgando en el mismo
        paso los que ya terminaron por su cuenta (limpieza automática:
        nunca queda una lista vacía almacenada).
        """
        with self._lock:
            entries = self._by_program.get(program, [])
            alive = [p for p in entries if p.is_alive()]
            if alive:
                self._by_program[program] = alive
            else:
                self._by_program.pop(program, None)
            return list(alive)

    def update(self, program: str, still_alive: list[TrackedProcess]) -> None:
        """Reemplaza el registro de `program` tras un intento de cierre."""
        with self._lock:
            if still_alive:
                self._by_program[program] = still_alive
            else:
                self._by_program.pop(program, None)


class SystemManager:
    """Abre, cierra, reinicia y consulta el estado de aplicaciones del SO."""

    _DISPATCHABLE_COMMANDS = frozenset(c.value for c in SystemCommand)

    def __init__(self) -> None:
        self.database = ProgramDatabase()
        self._registry = ProcessRegistry()

        logger.info(
            "[SystemManager] Inicializado. %d aplicaciones registradas.",
            len(self.database.list()),
        )

    # ==================================================
    # Router / dispatcher
    # ==================================================
    def execute(self, data: dict) -> ActionResult:
        """Despacha `data['command']` al método correspondiente de esta clase."""
        command = data.get("command")

        if command not in self._DISPATCHABLE_COMMANDS:
            return self._error(command, f"No existe la acción '{command}'.")

        method = getattr(self, command, None)
        if not callable(method):
            # Defensa en profundidad: no debería ocurrir si
            # _DISPATCHABLE_COMMANDS está sincronizado con los métodos
            # reales, pero se verifica de todas formas antes de invocar.
            logger.error("Comando '%s' está en la whitelist pero no es invocable.", command)
            return self._error(command, f"No existe la acción '{command}'.")

        return method(data)

    # ==================================================
    # Verificar existencia
    # ==================================================
    def exists(self, name: str) -> bool:
        """True si `name` corresponde a una aplicación registrada."""
        if not name:
            return False
        return self.database.find(name) is not None

    # ==================================================
    # Abrir aplicación
    # ==================================================
    def open(self, data: dict) -> ActionResult:
        """Abre la aplicación indicada en `data['topic']` y rastrea su proceso."""
        app = data.get("topic")
        if not app:
            return self._error("open", "No especificaste qué aplicación abrir.")

        program = self.database.find(app)
        if program is None:
            return self._error("open", f"No conozco la aplicación '{app}'.")

        try:
            popen = subprocess.Popen(program)
        except OSError as e:
            # Ejecutable no encontrado, ruta inválida, permisos: un
            # desenlace esperable del dominio.
            logger.warning("No pude abrir '%s' (%s): %s", app, program, e)
            return self._error("open", f"No pude abrir {app}.", error=str(e))
        except Exception as e:
            logger.exception("Error inesperado abriendo '%s' (%s).", app, program)
            return self._error("open", f"No pude abrir {app}.", error=str(e))

        self._registry.track(program, popen, app)

        return self._success(
            "open", f"Abriendo {app}...", data={"program": app, "pid": popen.pid}
        )

    def _close_by_name(self, app: str, program: str) -> ActionResult:
        candidates = [os.path.basename(program)]

        # Caso especial: calculadora moderna de Windows
        if candidates[0].lower() == "calc.exe":
            candidates.append("Calculator.exe")
            candidates.append("ApplicationFrameHost.exe")

        last_error = None

        for candidate in candidates:
            try:
                result = subprocess.run(
                    ["taskkill", "/IM", candidate, "/F"],
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT_SECONDS,
                )
                if result.returncode == 0:
                    return self._success("close", f"{app} cerrado correctamente.")
                else:
                    last_error = (result.stderr or "").strip()
                    logger.warning("taskkill no pudo cerrar '%s' (%s): %s", app, candidate, last_error)
            except subprocess.TimeoutExpired:
                logger.warning("taskkill no respondió a tiempo cerrando '%s' (%s).", app, candidate)
                last_error = "taskkill timeout"
            except Exception as e:
                logger.exception("Error inesperado ejecutando taskkill para '%s' (%s).", app, candidate)
                last_error = str(e)

        return self._error("close", f"No pude cerrar {app}.", error=last_error or "Ningún candidato respondió")

    def _close_tracked(
        self, app: str, program: str, tracked: list[TrackedProcess]
    ) -> ActionResult:
        """Cierra por PID los procesos que el propio asistente abrió."""
        closed: list[TrackedProcess] = []
        still_alive: list[TrackedProcess] = []
        failures: list[str] = []

        for entry in tracked:
            if self._terminate_and_wait(entry):
                closed.append(entry)
            else:
                still_alive.append(entry)
                failures.append(f"PID {entry.pid} sigue activo.")

        self._registry.update(program, still_alive)

        if not still_alive:
            return self._success("close", f"{app} cerrado correctamente.")

        message = (
            f"No pude cerrar completamente {app}." if closed else f"No pude cerrar {app}."
        )
        return self._error("close", message, error="; ".join(failures))

    def _terminate_and_wait(self, entry: TrackedProcess) -> bool:
        """
        Intenta cerrar el proceso de `entry`, esperando confirmación
        real antes de devolver True. Usa `logger.warning()` para
        desenlaces esperables (timeout, proceso ya inexistente) y
        `logger.exception()` solo para errores realmente inesperados.
        """
        popen = entry.popen
        try:
            popen.terminate()
            popen.wait(timeout=SUBPROCESS_TIMEOUT_SECONDS)
            return True

        except ProcessLookupError:
            logger.warning(
                "PID %s ('%s') ya no existía al intentar cerrarlo.",
                entry.pid, entry.app_alias,
            )
            return True

        except subprocess.TimeoutExpired:
            logger.warning(
                "PID %s ('%s') no respondió a terminate() en %ss; forzando kill().",
                entry.pid, entry.app_alias, SUBPROCESS_TIMEOUT_SECONDS,
            )
            try:
                popen.kill()
                popen.wait(timeout=SUBPROCESS_TIMEOUT_SECONDS)
                return True
            except subprocess.TimeoutExpired:
                logger.warning(
                    "PID %s ('%s') sigue activo incluso tras kill().",
                    entry.pid, entry.app_alias,
                )
                return False
            except Exception:
                logger.exception(
                    "Error inesperado forzando el cierre del PID %s ('%s').",
                    entry.pid, entry.app_alias,
                )
                return False

        except Exception:
            logger.exception(
                "Error inesperado cerrando el proceso PID %s ('%s').",
                entry.pid, entry.app_alias,
            )
            return False


    # ==================================================
    # Reiniciar aplicación
    # ==================================================
    def restart(self, data: dict) -> ActionResult:
        """
        Reinicia la aplicación indicada en `data['topic']`.

        Si no está abierta, simplemente la abre (no tiene sentido
        fallar un "reinicio" de algo que no estaba corriendo). Si está
        abierta, la cierra y luego la abre.
        """
        app = data.get("topic")
        if not app:
            return self._error("restart", "No especificaste qué aplicación reiniciar.")

        if not self._is_open_bool(app):
            return self.open(data)

        close_result = self.close(data)
        if not close_result.success:
            return close_result

        return self.open(data)

    # ==================================================
    # Verificar si está abierto
    # ==================================================
    def _is_open_bool(self, app: str) -> bool:
        """Helper interno que devuelve True/False si la app está abierta."""
        if not app:
            return False

        program = self.database.find(app)
        if program is None:
            return False

        if self._registry.alive_for(program):
            return True

        candidates = [program]
        if program.lower() == "calc.exe":
            candidates.append("Calculator.exe")
            candidates.append("ApplicationFrameHost.exe")

        try:
            for candidate in candidates:
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {candidate}"],
                    capture_output=True,
                    text=True,
                    timeout=SUBPROCESS_TIMEOUT_SECONDS,
                )
                if candidate.lower() in result.stdout.lower():
                    return True
            return False
        except Exception:
            return False


    def is_open(self, data: dict) -> ActionResult:   # 🔧 CORREGIDO: ahora devuelve ActionResult
        app = data.get("topic")
        if not app:
            return self._error("is_open", "No especificaste qué aplicación consultar.")

        if self._is_open_bool(app):
            return self._success("is_open", f"{app} está abierto.")
        else:
            return self._success("is_open", f"{app} no está abierto.")


    # ==================================================
    # Helpers de construcción de ActionResult (DRY)
    # ==================================================
    @staticmethod
    def _success(command: str, message: str, *, data: dict | None = None) -> ActionResult:
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module="system",
            command=command,
            message=message,
            data=data,
        )

    @staticmethod
    def _error(command: str | None, message: str, *, error: str | None = None) -> ActionResult:
        return ActionResult(
            success=False,
            status=ActionStatus.ERROR,
            module="system",
            command=command,
            message=message,
            error=error,
        )
    def close(self, data: dict) -> ActionResult:
        app = data.get("topic")
        if not app:
            return self._error("close", "No especificaste qué aplicación cerrar.")

        program = self.database.find(app)
        if program is None:
            return self._error("close", f"No conozco la aplicación '{app}'.")

        tracked = self._registry.alive_for(program)
        if tracked:
            return self._close_tracked(app, program, tracked)
        return self._close_by_name(app, program)

    