from datetime import datetime


class LoggerFormatter:

    def format(
        self,
        level,
        module,
        command,
        message
    ):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Puede llegar como Enum o string
        if hasattr(level, "value"):
            level = level.value

        level_name = str(level).upper()

        module_name = (module or "UNKNOWN").upper()
        command_name = command or "NONE"

        return (
            f"[{timestamp}] "
            f"{level_name} "
            f"{module_name}/{command_name} "
            f"-> {message}"
        )