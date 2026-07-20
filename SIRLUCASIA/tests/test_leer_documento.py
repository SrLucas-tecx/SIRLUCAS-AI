from app.service.document_manager import DocumentManager


def test_leer_documento():

    doc = DocumentManager()

    doc.create({

        "format": "txt",
        "topic": "lectura",
        "content": "Hola Mundo"

    })

    respuesta = doc.read({

        "topic": "lectura"

    })

    assert "Hola Mundo" in respuesta
    