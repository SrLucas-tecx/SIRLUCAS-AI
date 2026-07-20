from app.service.document_manager import DocumentManager


def test_varios_documentos():

    doc = DocumentManager()

    formatos = [

        "txt",
        "docx",
        "pdf",
        "json"

    ]

    for formato in formatos:

        respuesta = doc.create({

            "format": formato,
            "topic": "archivo_prueba",
            "content": "Hola"

        })

        assert "creado" in respuesta.lower()
        