from app.service.document_manager import DocumentManager


def test_listar():

    doc = DocumentManager()

    respuesta = doc.list({})

    assert respuesta is not None
    