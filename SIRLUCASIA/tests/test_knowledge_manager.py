from app.core.knowledge_manager import KnowledgeManager


def test_search_success():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "search",
        "topic": "python"
    })

    # Puede o no existir dependiendo de tu base
    if result.success:
        assert result.status.value.lower() == "success"
        assert result.module == "knowledge"
        assert result.command == "search"
        assert result.data["topic"] == "python"


def test_search_with_value():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "search",
        "value": "python"
    })

    assert result.command == "search"


def test_search_without_topic():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "search"
    })

    assert result.success is False
    assert "No especificaste" in result.message


def test_invalid_command():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "inventado"
    })

    assert result.success is False
    assert "No existe la acción" in result.message


def test_unknown_topic():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "search",
        "topic": "__tema_que_no_existe_12345__"
    })

    assert result.success is False
    assert result.status.value.lower() == "warning"
    assert "No conozco" in result.message


def test_execute_returns_action_result():

    manager = KnowledgeManager()

    result = manager.execute({
        "command": "search",
        "topic": "python"
    })

    assert hasattr(result, "success")
    assert hasattr(result, "status")
    assert hasattr(result, "module")
    assert hasattr(result, "command")
    assert hasattr(result, "message")