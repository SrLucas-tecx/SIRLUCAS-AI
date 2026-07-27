from app.core.event_bus import EventBus


def test_listener_exception():

    bus = EventBus()

    received = []

    def bad(data):

        raise Exception("error")

    def good(data):

        received.append(data)

    bus.subscribe(

        "event",

        bad

    )

    bus.subscribe(

        "event",

        good

    )

    bus.publish(

        "event",

        1

    )

    assert received == [1]