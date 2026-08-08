from enum import Enum


class ActionStatus(Enum):
    SUCCESS = "success"
    OK = "success"  # alias de SUCCESS
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"