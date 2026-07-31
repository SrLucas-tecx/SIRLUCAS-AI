import pytest
from app.core.assistant import Assistant


def test_assistant_name():
    assistant = Assistant()
    assert assistant.name == "SIRLUCAS AI"


def test_assistant_version():
    assistant = Assistant()
    assert assistant.version == "0.1"


def test_router_modules():
    assistant = Assistant()
    for module in ["memory", "document", "system", "knowledge", "web", "calculator", "history"]:
        assert module in assistant.router.modules


def test_event_bus():
    assistant = Assistant()
    assert assistant.event_bus.has_subscribers("action.executed")


def test_parser_exists():
    assistant = Assistant()
    assert assistant.parser is not None


def test_pipeline_exists():
    assistant = Assistant()
    assert assistant.pipeline is not None


def test_formatter_exists():
    assistant = Assistant()
    assert assistant.response_formatter is not None


def test_context_manager():
    assistant = Assistant()
    assert assistant.context.turn() == 0


def test_history_manager():
    assistant = Assistant()
    assert assistant.history.history() == []
def test_integration_pipeline():
    assistant = Assistant()

    # Flujo completo: Parser → Pipeline → Formatter
    message = assistant.parser.parse("qué es python")
    result = assistant.pipeline.execute(message)
    response = assistant.response_formatter.format(result)

    assert response is not None
    assert isinstance(response, str)
    assert "python" in response.lower()
