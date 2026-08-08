from app.core.conversation_manager import ConversationManager


def test_conversation_manager_builds_without_task_executor():
    # TaskExecutor exige (router, event_bus): construir ConversationManager
    # sin inyectarlo no debe lanzar TypeError.
    manager = ConversationManager()

    assert manager.task_executor is None


def test_run_task_without_executor_returns_none():
    manager = ConversationManager()

    assert manager._run_task({"command": "talk"}) is None


def test_unknown_command():
    manager = ConversationManager()

    respuesta = manager.execute({"command": "no_existe"})

    assert "No existe el comando" in respuesta
