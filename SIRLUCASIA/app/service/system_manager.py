import subprocess
from app.database.program_database import ProgramDatabase
from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus

# ==================================================
# SystemManager
# Encargado de abrir, cerrar y controlar programas
# ==================================================

class SystemManager:

    def __init__(self):
        self.database = ProgramDatabase()

        print("=" * 50)
        print("[SystemManager]")
        print(f"{len(self.database.list())} aplicaciones registradas.")
        print("=" * 50)

    # ==================================================
    # Router
    # ==================================================
    def execute(self, data):
        command = data.get("command")
        method = getattr(self, command, None)

        if method is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command=command,
                message=f"No existe la acción '{command}'."
            )

        return method(data)

    # ==================================================
    # Verificar existencia
    # ==================================================
    def exists(self, name):
        if not name:
            return False
        return self.database.find(name) is not None

    # ==================================================
    # Abrir aplicación
    # ==================================================
    def open(self, data):
        app = data.get("topic")

        if not app:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="open",
                message="No especificaste qué aplicación abrir."
            )

        program = self.database.find(app)

        if program is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="open",
                message=f"No conozco la aplicación '{app}'."
            )

        try:
            subprocess.Popen(program)
            return ActionResult(
                success=True,
                status=ActionStatus.SUCCESS,
                module="system",
                command="open",
                message=f"Abriendo {app}...",
                data={"program": app}
            )
        except Exception as e:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="open",
                message=f"No pude abrir {app}.",
                error=str(e)
            )

    # ==================================================
    # Cerrar aplicación
    # ==================================================
    def close(self, data):
        app = data.get("topic")

        if not app:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="close",
                message="No especificaste qué aplicación cerrar."
            )

        program = self.database.find(app)

        if program is None:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="close",
                message=f"No conozco la aplicación '{app}'."
            )

        try:
            result = subprocess.run(
                ["taskkill", "/IM", program, "/F"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    status=ActionStatus.SUCCESS,
                    module="system",
                    command="close",
                    message=f"{app} cerrado correctamente."
                )

            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="close",
                message=f"No pude cerrar {app}.",
                error=result.stderr.strip()
            )
        except Exception as e:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="close",
                message=f"No pude cerrar {app}.",
                error=str(e)
            )

    # ==================================================
    # Reiniciar aplicación
    # ==================================================
    def restart(self, data):
        app = data.get("topic")

        if not app:
            return ActionResult(
                success=False,
                status=ActionStatus.ERROR,
                module="system",
                command="restart",
                message="No especificaste qué aplicación reiniciar."
            )

        close_result = self.close(data)
        if not close_result.success:   # 👈 ahora usamos success
            return close_result

        open_result = self.open(data)
        return open_result

    # ==================================================
    # Verificar si está abierto
    # ==================================================
    def is_open(self, app):
        program = self.database.find(app)

        if program is None:
            return False

        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {program}"],
                capture_output=True,
                text=True
            )
            return program.lower() in result.stdout.lower()
        except Exception:
            return False
