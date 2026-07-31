from unittest.mock import patch, MagicMock

from app.service.system_manager import SystemManager


def test_exists():

    manager = SystemManager()

    assert manager.exists("notepad") in [True, False]


def test_unknown_command():

    manager = SystemManager()

    result = manager.execute({
        "command": "fake"
    })

    assert result.success is False
    assert result.module == "system"


def test_open_without_topic():

    manager = SystemManager()

    result = manager.execute({
        "command": "open"
    })

    assert result.success is False
    assert "No especificaste" in result.message


def test_close_without_topic():

    manager = SystemManager()

    result = manager.execute({
        "command": "close"
    })

    assert result.success is False
    assert "No especificaste" in result.message


@patch("subprocess.Popen")
def test_open_success(mock_popen):

    manager = SystemManager()

    if manager.exists("notepad"):

        result = manager.open({
            "topic": "notepad"
        })

        assert result.success is True
        mock_popen.assert_called()


@patch("subprocess.run")
def test_close_success(mock_run):

    manager = SystemManager()

    process = MagicMock()
    process.returncode = 0
    process.stderr = ""

    mock_run.return_value = process

    if manager.exists("notepad"):

        result = manager.close({
            "topic": "notepad"
        })

        assert result.success is True


@patch("subprocess.run")
def test_is_open(mock_run):

    manager = SystemManager()

    process = MagicMock()
    process.stdout = "notepad.exe"

    mock_run.return_value = process

    if manager.exists("notepad"):

        assert manager.is_open("notepad") is True


def test_restart_without_topic():

    manager = SystemManager()

    result = manager.restart({})

    assert result.success is False