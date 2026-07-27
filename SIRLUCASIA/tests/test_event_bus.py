from app.core.event_bus import EventBus


def test_subscribe_publish():

    bus = EventBus()

    received = []

    def callback(data):

        received.append(data)

    bus.subscribe(

        "test",

        callback

    )

    bus.publish(

        "test",

        {"value": 10}

    )

    assert received == [

        {"value": 10}

    ]