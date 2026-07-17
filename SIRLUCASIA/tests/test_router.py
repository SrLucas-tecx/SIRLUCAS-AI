from app.core.router import Router


def test_router_creation():

    router = Router()

    assert router is not None
    