from app.core.context_manager import ContextManager


def test_initial_state():

    context = ContextManager()

    assert context.turn() == 0
    assert context.topic() is None
    assert context.module() is None
    assert context.command() is None

    assert context.document() is None
    assert context.program() is None
    assert context.search() is None

    assert context.has_document() is False
    assert context.has_program() is False
    assert context.has_search() is False


def test_update_system():

    context = ContextManager()

    context.update({
        "module": "system",
        "command": "open",
        "topic": "notepad"
    })

    assert context.turn() == 1
    assert context.module() == "system"
    assert context.command() == "open"
    assert context.topic() == "notepad"

    assert context.program() == "notepad"
    assert context.has_program()


def test_update_document():

    context = ContextManager()

    context.update({
        "module": "document",
        "command": "open",
        "topic": "archivo.txt"
    })

    assert context.document() == "archivo.txt"
    assert context.has_document()


def test_update_knowledge():

    context = ContextManager()

    context.update({
        "module": "knowledge",
        "command": "search",
        "topic": "python"
    })

    assert context.search() == "python"
    assert context.has_search()


def test_update_web():

    context = ContextManager()

    context.update({
        "module": "web",
        "command": "search",
        "topic": "OpenAI"
    })

    assert context.search() == "OpenAI"
    assert context.has_search()


def test_multiple_updates():

    context = ContextManager()

    context.update({
        "module": "system",
        "command": "open",
        "topic": "notepad"
    })

    context.update({
        "module": "document",
        "command": "create",
        "topic": "reporte"
    })

    context.update({
        "module": "knowledge",
        "command": "search",
        "topic": "python"
    })

    assert context.turn() == 3

    assert context.program() == "notepad"
    assert context.document() == "reporte"
    assert context.search() == "python"


def test_clear():

    context = ContextManager()

    context.update({
        "module": "system",
        "command": "open",
        "topic": "notepad"
    })

    context.clear()

    assert context.turn() == 0

    assert context.topic() is None
    assert context.module() is None
    assert context.command() is None

    assert context.program() is None
    assert context.document() is None
    assert context.search() is None

    assert not context.has_program()
    assert not context.has_document()
    assert not context.has_search()