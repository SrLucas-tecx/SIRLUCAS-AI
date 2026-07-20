from app.service.document_manager import DocumentManager


def test_eliminar():

    doc = DocumentManager()

    doc.create({

        "format": "txt",
        "topic": "borrar",
        "content": "Hola"

    })

    respuesta = doc.delete({

        "topic": "borrar"

    })

    assert "eliminado" in respuesta.lower()
    