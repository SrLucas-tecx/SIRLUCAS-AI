from pathlib import Path
from datetime import datetime

from app.core.logger_formatter import LoggerFormatter
from app.core.logger_level import LoggerLevel


class Logger:

    def __init__(self):

        self.logs_path = Path("logs")

        self.logs_path.mkdir(

            exist_ok=True

        )

        self.formatter = LoggerFormatter()

    # ==========================
    # Archivo del día
    # ==========================

    def current_log(self):

        filename = datetime.now().strftime(

            "%Y-%m-%d.log"

        )

        return self.logs_path / filename

    # ==========================
    # Escritura
    # ==========================

    def _write(

        self,

        level,

        module,

        command,

        message

    ):

        line = self.formatter.format(

            level,

            module,

            command,

            message

        )

        with open(

            self.current_log(),

            "a",

            encoding="utf-8"

        ) as file:

            file.write(

                line + "\n"

            )

    # ==========================
    # Métodos públicos
    # ==========================

    def debug(

        self,

        module,

        command,

        message

    ):

        self._write(

            LoggerLevel.DEBUG,

            module,

            command,

            message

        )

    def info(

        self,

        module,

        command,

        message

    ):

        self._write(

            LoggerLevel.INFO,

            module,

            command,

            message

        )

    def warning(

        self,

        module,

        command,

        message

    ):

        self._write(

            LoggerLevel.WARNING,

            module,

            command,

            message

        )

    def error(

        self,

        module,

        command,

        message

    ):

        self._write(

            LoggerLevel.ERROR,

            module,

            command,

            message

        )

    def critical(

        self,

        module,

        command,

        message

    ):

        self._write(

            LoggerLevel.CRITICAL,

            module,

            command,

            message

        )
    def log(self, result):

        self._write(

        result.status.value,

        result.module,

        result.command,

        result.message

    )