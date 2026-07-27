from app.core.event_bus import EventBus


def test_unknown_event():

    bus = EventBus()

    bus.publish(

        "nothing"

    )