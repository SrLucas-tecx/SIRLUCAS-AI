from app.core.event_bus import EventBus


def test_subscribe():

    bus = EventBus()

    called = []

    def callback(data):
        called.append(data)

    bus.subscribe("test", callback)

    bus.publish("test", 10)

    assert called == [10]


def test_unsubscribe():

    bus = EventBus()

    called = []

    def callback(data):
        called.append(data)

    bus.subscribe("test", callback)

    bus.unsubscribe("test", callback)

    bus.publish("test", 100)

    assert called == []


def test_multiple_listeners():

    bus = EventBus()

    result = []

    bus.subscribe("event", lambda d: result.append(1))
    bus.subscribe("event", lambda d: result.append(2))
    bus.subscribe("event", lambda d: result.append(3))

    bus.publish("event")

    assert result == [1, 2, 3]


def test_clear():

    bus = EventBus()

    bus.subscribe("event", lambda d: None)

    bus.clear()

    assert bus.events() == []


def test_has_subscribers():

    bus = EventBus()

    assert bus.has_subscribers("x") is False

    bus.subscribe("x", lambda d: None)

    assert bus.has_subscribers("x") is True


def test_publish_without_listeners():

    bus = EventBus()

    bus.publish("nothing")

    assert True