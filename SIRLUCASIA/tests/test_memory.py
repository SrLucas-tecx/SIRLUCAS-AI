from app.core.memory_manager import MemoryManager
from app.core.action_result import ActionResult

def test_remember():
    memory = MemoryManager()

    response = memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Juan"
    })

    # Ahora response es ActionResult
    assert isinstance(response, ActionResult)
    assert "Recordaré" in response.message
    assert memory.memory["nombre"] == "Juan"


def test_recall():
    memory = MemoryManager()

    memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Juan"
    })

    response = memory.execute({
        "command": "recall",
        "key": "nombre"
    })

    assert isinstance(response, ActionResult)
    assert response.success is True
    assert response.message == "Juan"
    assert response.data["value"] == "Juan"


def test_forget():
    memory = MemoryManager()

    memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Juan"
    })

    response = memory.execute({
        "command": "forget",
        "key": "nombre"
    })

    assert isinstance(response, ActionResult)
    assert "olvidado" in response.message.lower()
    assert "nombre" not in memory.memory


def test_list_memories():
    memory = MemoryManager()

    memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Juan"
    })

    memory.execute({
        "command": "remember",
        "key": "edad",
        "value": "20"
    })

    response = memory.list_memories()

    assert isinstance(response, ActionResult)
    assert response.success is True
    assert response.data["nombre"] == "Juan"
    assert response.data["edad"] == "20"
