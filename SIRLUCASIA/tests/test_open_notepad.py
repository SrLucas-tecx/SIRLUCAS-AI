from unittest.mock import patch

from app.service.system_manager import SystemManager


@patch("subprocess.Popen")
def test_open_notepad(mock):

    system = SystemManager()

    response = system.open({
        "topic": "notepad"
    })

    assert response.success is True
    assert "Abriendo" in response.message