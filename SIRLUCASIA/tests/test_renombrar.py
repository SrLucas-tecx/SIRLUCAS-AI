from app.service.document_manager import DocumentManager


def test_renombrar():

    doc = DocumentManager()

    doc.create({

        "format": "txt",
        "topic": "viejo",
        "content": "Hola"

    })

    respuesta = doc.rename({

        "old_name": "viejo",
        "new_name": "nuevo"

    })

    assert "renombrado" in respuesta.lower()