from unittest.mock import patch

from app.service.system_manager import SystemManager


@patch("os.system")
def test_open_notepad(mock):

    system = SystemManager()

    respuesta = system.open({

        "topic": "notepad"

    })

    assert "abriendo" in respuesta.lower()
    