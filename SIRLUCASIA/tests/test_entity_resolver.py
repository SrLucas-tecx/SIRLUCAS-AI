from app.core.entity_resolver import EntityResolver


def test_system_entity():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "system",
        "topic": "notepad"
    })

    assert data["entity"]["type"] == "program"
    assert data["entity"]["value"] == "notepad"


def test_document_entity():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "document",
        "topic": "informe",
        "format": "pdf"
    })

    assert data["entity"]["type"] == "document"
    assert data["entity"]["name"] == "informe"
    assert data["entity"]["format"] == "pdf"


def test_memory_entity():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "memory",
        "key": "nombre"
    })

    assert data["entity"]["type"] == "memory"
    assert data["entity"]["key"] == "nombre"


def test_web_entity():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "web",
        "topic": "Python"
    })

    assert data["entity"]["type"] == "search"
    assert data["entity"]["query"] == "Python"


def test_knowledge_entity():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "knowledge",
        "topic": "IA"
    })

    assert data["entity"]["type"] == "knowledge"
    assert data["entity"]["query"] == "IA"


def test_unknown_module():

    resolver = EntityResolver()

    data = resolver.resolve({
        "module": "fake"
    })

    assert "entity" not in data


def test_invalid_data():

    resolver = EntityResolver()

    assert resolver.resolve("hola") == "hola"


def test_empty_dict():

    resolver = EntityResolver()

    data = resolver.resolve({})

    assert data == {}