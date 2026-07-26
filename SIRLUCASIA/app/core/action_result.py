from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.action_status import ActionStatus


@dataclass
class ActionResult:

    success: bool

    status: ActionStatus

    message: str

    module: str | None = None

    command: str | None = None

    data: Any = None

    error: str | None = None

    timestamp: datetime = field(default_factory=datetime.now)