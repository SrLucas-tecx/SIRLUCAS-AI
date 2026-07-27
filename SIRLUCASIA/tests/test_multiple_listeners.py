from app.core.event_bus import EventBus


def test_multiple_listeners():

    bus = EventBus()

    a = []

    b = []

    bus.subscribe(

        "event",

        lambda data: a.append(data)

    )

    bus.subscribe(

        "event",

        lambda data: b.append(data)

    )

    bus.publish(

        "event",

        100

    )

    assert a == [100]

    assert b == [100]