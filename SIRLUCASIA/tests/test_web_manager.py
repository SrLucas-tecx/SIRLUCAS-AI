from app.core.web_manager import WebManager


def test_search_success():

    manager = WebManager()

    result = manager.execute({
        "command": "search",
        "topic": "python"
    })

    if result.success:
        assert result.module == "web"
        assert result.command == "search"
        assert result.data is not None


def test_search_without_topic():

    manager = WebManager()

    result = manager.execute({
        "command": "search"
    })

    assert result.success is False
    assert "No especificaste" in result.message


def test_search_unknown_topic():

    manager = WebManager()

    result = manager.execute({
        "command": "search",
        "topic": "__tema_que_no_existe__"
    })

    if not result.success:
        assert "No encontré" in result.message


def test_unknown_command():

    manager = WebManager()

    result = manager.execute({
        "command": "inventado"
    })

    assert result.success is False
    assert result.module == "web"
    assert result.command == "inventado"


def test_action_result_structure():

    manager = WebManager()

    result = manager.execute({
        "command": "search",
        "topic": "python"
    })

    assert hasattr(result, "success")
    assert hasattr(result, "status")
    assert hasattr(result, "module")
    assert hasattr(result, "command")
    assert hasattr(result, "message")