from app.core.conversation_manager import ConversationManager


def test_conversation():

    manager = ConversationManager()

    respuesta = manager.execute({

        "command": "talk",
        "topic": "hola"

    })

    assert "Hola" in respuesta