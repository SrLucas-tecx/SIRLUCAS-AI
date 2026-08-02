import tempfile
import os
import pytest
from app.service.document_manager import DocumentManager
from app.core.action_result import ActionResult

@pytest.mark.parametrize("format_name,extension", [
    ("word", ".docx"),
    ("excel", ".xlsx"),
    ("markdown", ".md"),
    ("json", ".json"),
    ("txt", ".txt"),
    ("unsupported", None),  # caso inválido
])
def test_crear_documentos_varios_formatos(format_name, extension):
    tmp_dir = tempfile.mkdtemp()
    manager = DocumentManager()
    manager.path = tmp_dir

    comando = {
        "topic": "demo",
        "format": format_name,
        "content": "contenido de prueba"
    }

    result = manager.create(comando)

    if extension is None:
        # formato inválido
        assert result.success is False
        assert "formato" in result.message.lower()
    else:
        # formato válido
        assert result.success is True
        assert "creado" in result.message.lower()
        assert os.path.exists(os.path.join(tmp_dir, f"demo{extension}"))
