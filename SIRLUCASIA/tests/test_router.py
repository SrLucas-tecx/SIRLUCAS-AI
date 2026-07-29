from app.core.router import Router


class FakeModule:

    def __init__(self):
        self.called = False

    def execute(self, data):
        self.called = True
        return "OK"


class FakeMemory:

    def __init__(self):
        self.saved = False

    def remember(self, data):
        self.saved = True


class FakeDatabase:

    def find(self, topic):
        return True


class FakeSystem:

    def __init__(self):
        self.database = FakeDatabase()

    def open(self, data):
        return "PROGRAM OPEN"

    def close(self, data):
        return "PROGRAM CLOSED"


class FakeDocument:

    def exists(self, topic):
        return True

    def open(self, data):
        return "DOCUMENT OPEN"

    def close(self, data):
        return "DOCUMENT CLOSED"


def test_register_module():

    router = Router()

    module = FakeModule()

    router.register("test", module)

    assert "test" in router.modules


def test_route_execute():

    router = Router()

    module = FakeModule()

    router.register("test", module)

    result = router.route({
        "module": "test",
        "command": "run"
    })

    assert result == "OK"
    assert module.called


def test_unknown_module():

    router = Router()

    result = router.route({
        "module": "fake"
    })

    assert "No existe" in result


def test_invalid_data():

    router = Router()

    assert router.route("hola") == "Datos inválidos: se esperaba un diccionario."


def test_memory_called():

    router = Router()

    module = FakeModule()
    memory = FakeMemory()

    router.register("test", module)
    router.register("memory", memory)

    router.route({
        "module": "test"
    })

    assert memory.saved


def test_open_program():

    router = Router()

    router.register("system", FakeSystem())

    result = router.route({
        "command": "open",
        "topic": "notepad"
    })

    assert result == "PROGRAM OPEN"


def test_close_program():

    router = Router()

    router.register("system", FakeSystem())

    result = router.route({
        "command": "close",
        "topic": "notepad"
    })

    assert result == "PROGRAM CLOSED"


def test_open_document():

    router = Router()

    router.register("document", FakeDocument())

    result = router.route({
        "command": "open",
        "topic": "archivo.txt"
    })

    assert result == "DOCUMENT OPEN"


def test_close_document():

    router = Router()

    router.register("document", FakeDocument())

    result = router.route({
        "command": "close",
        "topic": "archivo.txt"
    })

    assert result == "DOCUMENT CLOSED"