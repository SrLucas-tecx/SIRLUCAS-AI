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

SUBPROCESS_TIMEOUT_SECONDS = 5


class SystemCommand(StrEnum):
    OPEN = "open"
    CLOSE = "close"
    RESTART = "restart"


@dataclass(slots=True)
class TrackedProcess:
    popen: subprocess.Popen
    app_alias: str
    opened_at: datetime = field(default_factory=datetime.now)

    @property
    def pid(self) -> int:
        return self.popen.pid

    def is_alive(self) -> bool:
        return self.popen.poll() is None


class ProcessRegistry:
    def __init__(self) -> None:
        self._by_program: dict[str, list[TrackedProcess]] = {}
        self._lock = threading.RLock()

    def track(self, program: str, popen: subprocess.Popen, app_alias: str) -> None:
        with self._lock:
            self._by_program.setdefault(program, []).append(
                TrackedProcess(popen=popen, app_alias=app_alias)
            )

    def alive_for(self, program: str) -> list[TrackedProcess]:
        with self._lock:
            entries = self._by_program.get(program, [])
            alive = [p for p in entries if p.is_alive()]
            if alive:
                self._by_program[program] = alive
            else:
                self._by_program.pop(program, None)
            return list(alive)

    def update(self, program: str, still_alive: list[TrackedProcess]) -> None:
        with self._lock:
            if still_alive:
                self._by_program[program] = still_alive
            else:
                self._by_program.pop(program, None)


class SystemManager:
    _DISPATCHABLE_COMMANDS = frozenset(c.value for c in SystemCommand)

    def __init__(self) -> None:
        self.database = ProgramDatabase()
        self._registry = ProcessRegistry()
        logger.info("[SystemManager] Inicializado. %d aplicaciones registradas.", len(self.database.list()))

    def execute(self, data: dict) -> ActionResult:
        command = data.get("command")
        if command not in self._DISPATCHABLE_COMMANDS:
            return self._error(command, f"No existe la acción '{command}'.")
        method = getattr(self, command, None)
        if not callable(method):
            logger.error("Comando '%s' está en la whitelist pero no es invocable.", command)
            return self._error(command, f"No existe la acción '{command}'.")
        return method(data)

    def exists(self, name: str) -> bool:
        if not name:
            return False
        return self.database.find(name) is not None

    def open(self, data: dict) -> ActionResult:
        app = data.get("topic")
        if not app:
            return self._error("open", "No especificaste qué aplicación abrir.")
        program = self.database.find(app)
        if program is None:
            return self._error("open", f"No conozco la aplicación '{app}'.")
        try:
            popen = subprocess.Popen(
                [program],
                shell=False,
                close_fds=False
            )
        except OSError as e:
            logger.warning("No pude abrir '%s' (%s): %s", app, program, e)
            return self._error("open", f"No pude abrir {app}.", error=str(e))
        except Exception as e:
            logger.exception("Error inesperado abriendo '%s' (%s).", app, program)
            return self._error("open", f"No pude abrir {app}.", error=str(e))
        self._registry.track(program, popen, app)
        return self._success("open", f"Abriendo {app}...", data={"program": app, "pid": popen.pid})

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

    def _close_tracked(self, app: str, program: str, tracked: list[TrackedProcess]) -> ActionResult:
        closed, still_alive, failures = [], [], []
        for entry in tracked:
            if self._terminate_and_wait(entry):
                closed.append(entry)
            else:
                still_alive.append(entry)
                failures.append(f"PID {entry.pid} sigue activo.")
        self._registry.update(program, still_alive)
        if not still_alive:
            return self._success("close", f"{app} cerrado correctamente.")
        message = f"No pude cerrar completamente {app}." if closed else f"No pude cerrar {app}."
        return self._error("close", message, error="; ".join(failures))

    def _terminate_and_wait(self, entry: TrackedProcess) -> bool:
        popen = entry.popen
        try:
            popen.terminate()
            popen.wait(timeout=SUBPROCESS_TIMEOUT_SECONDS)
            return True
        except ProcessLookupError:
            logger.warning("PID %s ('%s') ya no existía al intentar cerrarlo.", entry.pid, entry.app_alias)
            return True
        except subprocess.TimeoutExpired:
            logger.warning("PID %s ('%s') no respondió a terminate(); forzando kill().", entry.pid, entry.app_alias)
            try:
                popen.kill()
                popen.wait(timeout=SUBPROCESS_TIMEOUT_SECONDS)
                return True
            except subprocess.TimeoutExpired:
                logger.warning("PID %s ('%s') sigue activo incluso tras kill().", entry.pid, entry.app_alias)
                return False
            except Exception:
                logger.exception("Error inesperado forzando el cierre del PID %s ('%s').", entry.pid, entry.app_alias)
                return False
        except Exception:
            logger.exception("Error inesperado cerrando el proceso PID %s ('%s').", entry.pid, entry.app_alias)
            return False

    def _close_by_name(self, app: str, program: str) -> ActionResult:
        try:
            result = subprocess.run(
                ["taskkill", "/IM", program, "/F"],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            logger.warning("taskkill no respondió a tiempo cerrando '%s' (%s).", app, program)
            return self._error("close", f"No pude cerrar {app}.", error="taskkill no respondió...")
        except Exception as e:
            logger.exception("Error inesperado ejecutando taskkill para '%s' (%s).", app, program)
            return self._error("close", f"No pude cerrar {app}.", error=str(e))
        if result.returncode == 0:
            return self._success("close", f"{app} cerrado correctamente.")
        stderr = (result.stderr or "").strip()
        stderr_lower = stderr.casefold()
        if "not found" in stderr_lower or "no se encontro" in stderr_lower:
            return self._error("close", f"{app} no está abierto.", error=stderr)
        if "denied" in stderr_lower or "denegado" in stderr_lower:
            return self._error("close", f"No tengo permisos para cerrar {app}.", error=stderr)
        logger.warning("taskkill no pudo cerrar '%s' (%s): %s", app, program, stderr)
        return self._error("close", f"No pude cerrar {app}.", error=stderr)

    def restart(self, data: dict) -> ActionResult:
        app = data.get("topic")
        if not app:
            return self._error("restart", "No especificaste qué aplicación reiniciar.")
        if not self.is_open(app):
            return self.open(data)
        close_result = self.close(data)
        if not close_result.success:
            return close_result
        return self.open(data)

    def is_open(self, app: str) -> bool:
        if not app:
            return False
        program = self.database.find(app)
        if program is None:
            return False
        if self._registry.alive_for(program):
            return True
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {program}"],
                capture_output=True,
                text=True,
                timeout=SUBPROCESS_TIMEOUT_SECONDS,
            )
            lines = result.stdout.lower().splitlines()
            return any(line.strip().startswith(program.lower()) for line in lines)
        except subprocess.TimeoutExpired:
            logger.warning("tasklist no respondió a tiempo consultando '%s'.", program)
            return False
        except Exception:
            logger.exception("No se pudo consultar tasklist para '%s'.", program)
            return False

    @staticmethod
    def _success(command: str, message: str, *, data: dict | None = None) -> ActionResult:
        return ActionResult(success=True, status=ActionStatus.SUCCESS, module="system", command=command, message=message, data=data)

    @staticmethod
    def _error(
        command: str | None,
        message: str,
        *,
        error: str | None = None,
        data: dict | None = None,
    ) -> ActionResult:
        return ActionResult(
            success=False,
            status=ActionStatus.ERROR,
            module="system",
            command=command,
            message=message,
            error=error,
            data=data,
        )