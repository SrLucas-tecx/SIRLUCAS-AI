from app.service.document_manager import DocumentManager


def test_copiar():

    doc = DocumentManager()

    doc.create({

        "format": "txt",
        "topic": "origen",
        "content": "Hola"

    })

    respuesta = doc.copy({

        "old_name": "origen",
        "new_name": "copia"

    })

    assert "copiado" in respuesta.lower()