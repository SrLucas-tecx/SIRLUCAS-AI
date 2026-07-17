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
def test_create_txt():

    manager = DocumentManager()

    result = manager.create({

        "topic": "test_txt",
        "format": "txt",
        "content": "Hola"

    })

    assert "creado" in result.lower()

def test_create_docx():

    manager = DocumentManager()

    result = manager.create({

        "topic": "test_docx",
        "format": "word",
        "content": "Hola Word"

    })

    assert "creado" in result.lower()

def test_create_pdf():
    
        manager = DocumentManager()
    
        result = manager.create({
    
            "topic": "test_pdf",
            "format": "pdf",
            "content": "Hola PDF"
    
        })
    
        assert "creado" in result.lower()
def test_create_excel():
    
        manager = DocumentManager()
    
        result = manager.create({
    
            "topic": "test_excel",
            "format": "excel",
            "content": "Uno\nDos\nTres"
    
        })
    
        assert "creado" in result.lower()

def test_create_json():

    manager = DocumentManager()

    result = manager.create({

        "topic": "test_json",
        "format": "json",
        "content": '{"nombre":"Juan"}'

    })

    assert "creado" in result.lower()

def test_read_document():

    manager = DocumentManager()

    manager.create({

        "topic": "leer_test",
        "format": "txt",
        "content": "Hola"

    })

    result = manager.read({

        "topic": "leer_test"

    })

    assert result == "Hola"

def test_delete_document():

    manager = DocumentManager()

    manager.create({

        "topic": "eliminar_test",
        "format": "txt",
        "content": "Hola"

    })

    result = manager.delete({

        "topic": "eliminar_test"

    })

    assert "eliminado" in result.lower()