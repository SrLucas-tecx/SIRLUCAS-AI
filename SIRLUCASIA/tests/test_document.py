from app.service.document_manager import DocumentManager


def test_create_document():

    manager = DocumentManager()

    data = {
        "topic": "pytest_document",
        "content": "Hola Mundo"
    }

    response = manager.create(data)

    assert "creado" in response.lower()


def test_read_document():

    manager = DocumentManager()

    data = {
        "topic": "pytest_document"
    }

    response = manager.read(data)

    assert "Hola Mundo" in response


def test_delete_document():

    manager = DocumentManager()

    data = {
        "topic": "pytest_document"
    }

    response = manager.delete(data)

    assert "eliminado" in response.lower()