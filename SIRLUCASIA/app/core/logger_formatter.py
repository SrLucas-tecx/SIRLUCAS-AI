from datetime import datetime


class LoggerFormatter:

    def format(

        self,

        level,

        module,

        command,

        message

    ):

        timestamp = datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        )

        return (

            f"[{timestamp}] "

            f"{level.value} "

            f"{module.upper()}/{command} "

            f"-> {message}"

        )