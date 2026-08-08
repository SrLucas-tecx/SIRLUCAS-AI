import pytest

from app.core.intent_resolver import IntentResolver


def test_open_program():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "system",
        "command": "open"
    })

    assert data["intent"] == "OPEN_PROGRAM"


def test_close_program():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "system",
        "command": "close"
    })

    assert data["intent"] == "CLOSE_PROGRAM"


def test_create_document():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "document",
        "command": "create"
    })

    assert data["intent"] == "CREATE_DOCUMENT"


def test_write_document():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "document",
        "command": "write"
    })

    assert data["intent"] == "WRITE_DOCUMENT"


def test_read_document():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "document",
        "command": "read"
    })

    assert data["intent"] == "READ_DOCUMENT"


def test_delete_document():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "document",
        "command": "delete"
    })

    assert data["intent"] == "DELETE_DOCUMENT"


def test_search_knowledge():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "knowledge"
    })

    assert data["intent"] == "SEARCH_KNOWLEDGE"


def test_search_web():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "web"
    })

    assert data["intent"] == "SEARCH_WEB"


def test_calculate():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "calculator"
    })

    assert data["intent"] == "CALCULATE"


def test_save_memory():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "memory",
        "command": "remember"
    })

    assert data["intent"] == "SAVE_MEMORY"


def test_read_memory():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "memory",
        "command": "recall"
    })

    assert data["intent"] == "READ_MEMORY"


def test_chat():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "conversation"
    })

    assert data["intent"] == "CHAT"


def test_restart_program():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "system",
        "command": "restart"
    })

    assert data["intent"] == "RESTART_PROGRAM"


@pytest.mark.parametrize(
    "command, intent",
    [
        ("rename", "RENAME_DOCUMENT"),
        ("copy", "COPY_DOCUMENT"),
        ("move", "MOVE_DOCUMENT"),
        ("list_documents", "LIST_DOCUMENTS"),
        ("info", "INFO_DOCUMENT"),
        ("search", "SEARCH_DOCUMENT"),
        ("modified", "MODIFIED_DOCUMENT"),
    ],
)
def test_document_commands(command, intent):

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "document",
        "command": command
    })

    assert data["intent"] == intent


def test_list_memory():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "memory",
        "command": "list"
    })

    assert data["intent"] == "LIST_MEMORY"


@pytest.mark.parametrize(
    "command, intent",
    [
        ("history", "READ_HISTORY"),
        ("last", "LAST_HISTORY"),
        ("search", "SEARCH_HISTORY"),
        ("clear", "CLEAR_HISTORY"),
    ],
)
def test_history_commands(command, intent):

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "history",
        "command": command
    })

    assert data["intent"] == intent


def test_unknown_module():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "fake"
    })

    assert data["intent"] == "UNKNOWN"
    assert data["module"] == "unknown"


def test_unknown_command_falls_back_to_unknown():

    resolver = IntentResolver()

    data = resolver.resolve({
        "module": "system",
        "command": "no_existe"
    })

    assert data["intent"] == "UNKNOWN"
    assert data["module"] == "unknown"


def test_invalid_data():

    resolver = IntentResolver()

    assert resolver.resolve("hola") == "hola"