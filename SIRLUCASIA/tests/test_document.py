import pytest
from app.service.document_manager import DocumentManager


# ==================================================
# Flujo completo: creación, escritura, lectura, eliminación
# ==================================================

def test_create_write_read_delete():
    manager = DocumentManager()

    manager.create({"topic": "pytest_demo"})
    manager.write({"topic": "pytest_demo", "content": "Hola Mundo"})

    result = manager.read({"topic": "pytest_demo"})
    assert "Hola Mundo" in result

    manager.delete({"topic": "pytest_demo"})
    assert manager.exists("pytest_demo") is False


# ==================================================
# Renombrar documento
# ==================================================

def test_rename_document():
    manager = DocumentManager()

    manager.create({"topic": "doc1"})
    manager.rename({"old_name": "doc1", "new_name": "doc2"})

    assert manager.exists("doc2")


# ==================================================
# Copiar documento
# ==================================================

def test_copy_document():
    manager = DocumentManager()

    manager.create({"topic": "original"})
    manager.copy({"old_name": "original", "new_name": "copia"})

    assert manager.exists("original")
    assert manager.exists("copia")
