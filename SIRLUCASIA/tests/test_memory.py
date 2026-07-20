from app.core.memory_manager import MemoryManager


def test_remember():

    memory = MemoryManager()

    response = memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Juan"
    })

    assert "Recordaré" in response
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

    assert response == "Juan"


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

    assert "olvidado" in response.lower()
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

    memories = memory.list_memories()

    assert memories["nombre"] == "Juan"
    assert memories["edad"] == "20"