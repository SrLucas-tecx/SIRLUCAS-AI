from app.core.web_manager import WebManager


def test_web_creation():

    manager = WebManager()

    assert manager is not None