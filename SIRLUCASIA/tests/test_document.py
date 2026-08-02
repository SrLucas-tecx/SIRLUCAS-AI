import os
import pytest
from app.service.document_manager import DocumentManager
from app.core.action_result import ActionResult
from app.modules.parser import Parser
from app.core.router import Router
from app.core.memory_manager import MemoryManager
from app.service.system_manager import SystemManager
from app.core.knowledge_manager import KnowledgeManager
from app.core.web_manager import WebManager


def crear_router():
    router = Router()
    router.register("memory", MemoryManager())
    router.register("document", DocumentManager())
    router.register("system", SystemManager())
    router.register("knowledge", KnowledgeManager())
    router.register("web", WebManager())
    return router


def test_document_manager_full_cycle():
    manager = DocumentManager()
    manager.path = "documents"

    # 1. Crear documento
    result_create = manager.create({
        "topic": "demo",
        "format": "txt",
        "content": "Hola mundo"
    })
    assert isinstance(result_create, ActionResult)
    assert result_create.success is True
    assert "creado" in result_create.message.lower()
    assert os.path.exists(os.path.join(manager.path, "demo.txt"))

    # 2. Leer documento
    result_read = manager.read({"topic": "demo"})
    assert isinstance(result_read, ActionResult)
    assert result_read.success is True
    assert "contenido" in result_read.message.lower()
    assert "Hola mundo" in result_read.data["content"]

    # 3. Escribir documento
    result_write = manager.write({"topic": "demo", "content": "Nueva línea"})
    assert isinstance(result_write, ActionResult)
    assert result_write.success is True
    assert "contenido" in result_write.message.lower()

    # 4. Renombrar documento
    result_rename = manager.rename({"old_name": "demo", "new_name": "renombrado"})
    assert isinstance(result_rename, ActionResult)
    assert result_rename.success is True
    assert "renombrado" in result_rename.message.lower()
    assert os.path.exists(os.path.join(manager.path, "renombrado.txt"))

    # 5. Copiar documento
    result_copy = manager.copy({"old_name": "renombrado", "new_name": "copia"})
    assert isinstance(result_copy, ActionResult)
    assert result_copy.success is True
    assert "copiado" in result_copy.message.lower()
    assert os.path.exists(os.path.join(manager.path, "copia.txt"))

    # 6. Mover documento
    new_dir = "documents/movidos"
    os.makedirs(new_dir, exist_ok=True)
    result_move = manager.move({"topic": "copia", "new_path": new_dir})
    assert isinstance(result_move, ActionResult)
    assert result_move.success is True
    assert "movido" in result_move.message.lower()
    assert os.path.exists(os.path.join(new_dir, "copia.txt"))

    # 7. Listar documentos
    result_list = manager.list_documents()
    assert isinstance(result_list, ActionResult)
    assert result_list.success is True
    assert "renombrado.txt" in result_list.data

    # 8. Info del documento
    result_info = manager.info({"topic": "renombrado"})
    assert isinstance(result_info, ActionResult)
    assert result_info.success is True
    assert result_info.data["name"] == "renombrado.txt"

    # 9. Última modificación
    result_mod = manager.modified({"topic": "renombrado"})
    assert isinstance(result_mod, ActionResult)
    assert result_mod.success is True
    assert "modified" in result_mod.data

    # 10. Eliminar documento
    result_delete = manager.delete({"topic": "renombrado"})
    assert isinstance(result_delete, ActionResult)
    assert result_delete.success is True
    assert "eliminado" in result_delete.message.lower()
    assert not os.path.exists(os.path.join(manager.path, "renombrado.txt"))


def test_crear_documento_sin_contenido():
    router = crear_router()
    comando = {
        "module": "document",
        "command": "create",
        "topic": "vacio",
        "format": "word",
        "content": ""
    }
    respuesta = router.route(comando)
    assert respuesta.success is False
    assert "contenido" in respuesta.message.lower()


def test_crear_documento_formato_invalido():
    router = crear_router()
    comando = {
        "module": "document",
        "command": "create",
        "topic": "demo",
        "format": "unsupported",
        "content": "texto"
    }
    respuesta = router.route(comando)
    assert respuesta.success is False
    assert "formato" in respuesta.message.lower()


def test_crear_documento_duplicado():
    manager = DocumentManager()
    manager.path = "documents"

    router = crear_router()
    comando = {
        "module": "document",
        "command": "create",
        "topic": "demo",
        "format": "word",
        "content": "hola mundo"
    }
    respuesta1 = router.route(comando)
    assert respuesta1.success is True

    respuesta2 = router.route(comando)
    assert respuesta2.success is False
    assert "ya existe" in respuesta2.message.lower()


def test_crear_documento_nombre_invalido():
    router = crear_router()
    comando = {
        "module": "document",
        "command": "create",
        "topic": "###",
        "format": "word",
        "content": "hola mundo"
    }
    respuesta = router.route(comando)
    assert respuesta.success is False
    assert "nombre" in respuesta.message.lower()


# 🔥 Nuevo bloque: creación de múltiples formatos en documents
@pytest.mark.parametrize("format_name,extension", [
    ("word", ".docx"),
    ("excel", ".xlsx"),
    ("pdf", ".pdf"),
    ("markdown", ".md"),
    ("json", ".json"),
    ("txt", ".txt"),
])
def test_crear_varios_formatos_en_documents(format_name, extension):
    manager = DocumentManager()
    manager.path = "documents"

    comando = {
        "topic": f"demo_{format_name}",
        "format": format_name,
        "content": "contenido de prueba"
    }

    result = manager.create(comando)
    assert result.success is True
    assert os.path.exists(os.path.join(manager.path, f"demo_{format_name}{extension}"))
