from app.core.task_executor import TaskExecutor


class FakeAction:

    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data


class FakeRouter:

    def __init__(self):
        self.called = False

    def route(self, data):
        self.called = True
        return f"RESULTADO: {data['command']}"


class FakeEventBus:

    def __init__(self):
        self.called = False
        self.event = None
        self.data = None

    def publish(self, event, data):
        self.called = True
        self.event = event
        self.data = data


def test_execute_actions():

    router = FakeRouter()
    event_bus = FakeEventBus()

    executor = TaskExecutor(router, event_bus)

    actions = [
        FakeAction({
            "module": "system",
            "command": "open",
            "topic": "notepad"
        })
    ]

    results = executor.execute(actions)

    assert router.called is True
    assert event_bus.called is True
    assert event_bus.event == "action.executed"
    assert results == ["RESULTADO: open"]


def test_multiple_actions():

    router = FakeRouter()
    event_bus = FakeEventBus()

    executor = TaskExecutor(router, event_bus)

    actions = [
        FakeAction({"command": "uno"}),
        FakeAction({"command": "dos"}),
        FakeAction({"command": "tres"}),
    ]

    results = executor.execute(actions)

    assert len(results) == 3
    assert results[0] == "RESULTADO: uno"
    assert results[1] == "RESULTADO: dos"
    assert results[2] == "RESULTADO: tres"


def test_publish_exception_does_not_stop_execution():

    router = FakeRouter()

    class BrokenEventBus:
        def publish(self, event, data):
            raise Exception("Error")

    executor = TaskExecutor(router, BrokenEventBus())

    actions = [
        FakeAction({"command": "open"})
    ]

    results = executor.execute(actions)

    assert results == ["RESULTADO: open"]