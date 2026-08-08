from app.core.action_result import ActionResult
from app.core.action_status import ActionStatus
from app.core.task_executor import TaskExecutor


class FakeAction:

    def __init__(self, data):
        self.data = data

    def to_dict(self):
        return self.data

    def complete(self):
        pass

    def fail(self):
        pass


class FakeRouter:

    def __init__(self):
        self.called = False

    def route(self, data):
        self.called = True
        return ActionResult(
            success=True,
            status=ActionStatus.SUCCESS,
            module=data.get("module"),
            command=data.get("command"),
            message=f"RESULTADO: {data['command']}",
        )


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
    assert [r.message for r in results] == ["RESULTADO: open"]


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
    assert [r.message for r in results] == [
        "RESULTADO: uno",
        "RESULTADO: dos",
        "RESULTADO: tres",
    ]


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

    assert [r.message for r in results] == ["RESULTADO: open"]


def test_router_none_publishes_error_result():

    class NoneRouter:
        def route(self, data):
            return None

    event_bus = FakeEventBus()
    executor = TaskExecutor(NoneRouter(), event_bus)

    results = executor.execute([FakeAction({"module": "system", "command": "open"})])

    assert isinstance(results[0], ActionResult)
    assert results[0].success is False
    assert event_bus.data is results[0]


def test_router_exception_publishes_error_result():

    class BrokenRouter:
        def route(self, data):
            raise RuntimeError("boom")

    event_bus = FakeEventBus()
    executor = TaskExecutor(BrokenRouter(), event_bus)

    results = executor.execute([FakeAction({"module": "system", "command": "open"})])

    assert isinstance(results[0], ActionResult)
    assert results[0].success is False
    assert results[0].error == "boom"
    assert event_bus.data is not None