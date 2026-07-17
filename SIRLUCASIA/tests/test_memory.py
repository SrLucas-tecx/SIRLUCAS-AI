from app.core.memory_manager import MemoryManager


def test_remember():

    memory = MemoryManager()

    memory.remember("nombre", "Juan")

    assert memory.recall("nombre") == "Juan"


def test_forget():

    memory = MemoryManager()

    memory.remember("edad", "20")

    assert memory.forget("edad") is True

    assert memory.recall("edad") is None


def test_list_memories():

    memory = MemoryManager()

    memory.remember("ciudad", "Toluca")

    memories = memory.list_memories()

    assert "ciudad" in memories