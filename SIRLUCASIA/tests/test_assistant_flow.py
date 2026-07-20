from app.modules.parser import Parser
from app.core.router import Router

from app.core.memory_manager import MemoryManager
from app.service.document_manager import DocumentManager
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


def test_crear_documento():

    parser = Parser()
    router = crear_router()

    comando = parser.parse(
        "crea un word prueba con el texto hola mundo"
    )

    respuesta = router.route(comando)

    assert "creado" in respuesta.lower()


def test_guardar_memoria():

    parser = Parser()
    router = crear_router()

    comando = parser.parse("me llamo Juan")

    respuesta = router.route(comando)

    assert respuesta is not None


def test_recordar_memoria():

    parser = Parser()
    router = crear_router()

    router.route(parser.parse("me llamo Juan"))

    respuesta = router.route(
        parser.parse("como me llamo")
    )

    assert respuesta.lower() == "juan"