from app.core.action_status import ActionStatus
from app.core.chat_manager import ChatManager, PLACEHOLDER_MESSAGE
from app.core.router import Router


def test_chat_manager_returns_placeholder():
    manager = ChatManager()

    result = manager.execute({
        "module": "conversation",
        "command": "talk",
        "topic": "hola"
    })

    assert result.success is True
    assert result.status == ActionStatus.OK
    assert result.module == "conversation"
    assert result.command == "chat"
    assert result.message == PLACEHOLDER_MESSAGE


def test_router_routes_conversation():
    router = Router()
    router.register("conversation", ChatManager())

    result = router.route({
        "module": "conversation",
        "command": "unknown",
        "topic": "algo que no entiendo"
    })

    assert result.success is True
    assert "No existe el módulo" not in result.message
