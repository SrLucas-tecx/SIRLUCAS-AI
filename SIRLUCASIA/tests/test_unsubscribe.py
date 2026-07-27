from app.core.event_bus import EventBus


def test_unsubscribe():

    bus = EventBus()

    received = []

    def callback(data):

        received.append(data)

    bus.subscribe(

        "test",

        callback

    )

    bus.unsubscribe(

        "test",

        callback

    )

    bus.publish(

        "test",

        123

    )

    assert received == []