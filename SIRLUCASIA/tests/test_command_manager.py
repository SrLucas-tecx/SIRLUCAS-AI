from app.core.command_manager import CommandManager


class FakeMemory:

    def __init__(self):
        self.calls = []

    def remember(self, data):
        self.calls.append(data)


def test_remember_passes_dict_to_memory():
    memory = FakeMemory()
    manager = CommandManager(memory)

    respuesta = manager.execute({
        "command": "remember",
        "key": "ciudad",
        "value": "Bogotá"
    })

    assert memory.calls == [{"key": "ciudad", "value": "Bogotá"}]
    assert "Lo recordaré" in respuesta
