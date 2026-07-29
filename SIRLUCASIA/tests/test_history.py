from app.core.history_manager import HistoryManager


def test_history_add():

    history = HistoryManager()

    history.clear()

    history.add(
        module="system",
        command="open",
        topic="notepad"
    )

    data = history.history()

    assert len(data) == 1
    assert data[0]["module"] == "system"
    assert data[0]["command"] == "open"
    assert data[0]["topic"] == "notepad"


def test_history_last():

    history = HistoryManager()

    history.clear()

    history.add(
        module="document",
        command="create",
        topic="informe"
    )

    last = history.last()

    assert last["module"] == "document"
    assert last["command"] == "create"
    assert last["topic"] == "informe"


def test_history_clear():

    history = HistoryManager()

    history.add(
        module="memory",
        command="remember",
        topic="nombre"
    )

    history.clear()

    assert history.history() == []


def test_history_multiple_commands():

    history = HistoryManager()

    history.clear()

    history.add(
        module="system",
        command="open",
        topic="notepad"
    )

    history.add(
        module="document",
        command="create",
        topic="informe"
    )

    history.add(
        module="knowledge",
        command="search",
        topic="python"
    )

    data = history.history()

    assert len(data) == 3

    assert data[0]["topic"] == "notepad"
    assert data[1]["topic"] == "informe"
    assert data[2]["topic"] == "python"


def test_history_last_empty():

    history = HistoryManager()

    history.clear()

    assert history.last() is None


def test_execute_history():

    history = HistoryManager()

    history.clear()

    history.add(
        module="system",
        command="open",
        topic="notepad"
    )

    result = history.execute({
        "command": "history"
    })

    assert len(result) == 1
    assert result[0]["module"] == "system"


def test_execute_last():

    history = HistoryManager()

    history.clear()

    history.add(
        module="document",
        command="create",
        topic="informe"
    )

    result = history.execute({
        "command": "last"
    })

    assert result["module"] == "document"
    assert result["command"] == "create"


def test_execute_unknown_command():

    history = HistoryManager()

    result = history.execute({
        "command": "fake"
    })

    assert result is None