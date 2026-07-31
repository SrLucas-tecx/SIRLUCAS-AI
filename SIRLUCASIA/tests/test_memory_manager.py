from app.core.memory_manager import MemoryManager


def test_remember():

    memory = MemoryManager()
    memory.clear()

    result = memory.remember({
        "key": "nombre",
        "value": "Juan"
    })

    assert "Recordaré" in result
    assert memory.recall({"key": "nombre"}) == "Juan"


def test_recall_not_found():

    memory = MemoryManager()
    memory.clear()

    result = memory.recall({
        "key": "edad"
    })

    assert "No recuerdo" in result


def test_forget():

    memory = MemoryManager()
    memory.clear()

    memory.remember({
        "key": "ciudad",
        "value": "Toluca"
    })

    result = memory.forget({
        "key": "ciudad"
    })

    assert "He olvidado" in result
    assert memory.exists({"key": "ciudad"}) is False


def test_exists():

    memory = MemoryManager()
    memory.clear()

    memory.remember({
        "key": "color",
        "value": "azul"
    })

    assert memory.exists({"key": "color"}) is True
    assert memory.exists({"key": "otro"}) is False


def test_keys_values():

    memory = MemoryManager()
    memory.clear()

    memory.remember({
        "key": "uno",
        "value": 1
    })

    memory.remember({
        "key": "dos",
        "value": 2
    })

    assert "uno" in memory.keys()
    assert "dos" in memory.keys()

    assert 1 in memory.values()
    assert 2 in memory.values()


def test_list_memories():

    memory = MemoryManager()
    memory.clear()

    memory.remember({
        "key": "pais",
        "value": "México"
    })

    memories = memory.list_memories()

    assert isinstance(memories, dict)
    assert memories["pais"] == "México"


def test_clear():

    memory = MemoryManager()

    memory.remember({
        "key": "a",
        "value": "b"
    })

    result = memory.clear()

    assert result == "Memoria limpiada correctamente."
    assert memory.list_memories() == "La memoria está vacía."


def test_execute_dispatch():

    memory = MemoryManager()
    memory.clear()

    result = memory.execute({
        "command": "remember",
        "key": "nombre",
        "value": "Lucas"
    })

    assert "Recordaré" in result


def test_execute_invalid_command():

    memory = MemoryManager()

    result = memory.execute({
        "command": "inexistente"
    })

    assert "No existe el comando" in result


def test_missing_key():

    memory = MemoryManager()

    assert "clave" in memory.remember({
        "value": "Juan"
    })

    assert "recordar" in memory.recall({})

    assert "olvidar" in memory.forget({})


def test_missing_value():

    memory = MemoryManager()

    result = memory.remember({
        "key": "nombre"
    })

    assert "valor" in result