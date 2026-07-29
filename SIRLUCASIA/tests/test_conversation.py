from app.core.conversation_manager import ConversationManager
from app.core.action_status import ActionStatus


def test_conversation():
    manager = ConversationManager()

    respuesta = manager.execute({
        "command": "talk",
        "topic": "hola"
    })

    assert "Hola" in respuesta.message
    assert respuesta.success is True
    assert respuesta.module == "conversation"
    assert respuesta.command == "talk"
    assert respuesta.status == ActionStatus.SUCCESS