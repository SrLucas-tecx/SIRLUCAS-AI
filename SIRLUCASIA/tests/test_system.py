from app.service.system_manager import SystemManager


def test_system_exists():

    system = SystemManager()

    assert "notepad" in system.apps


def test_unknown_program():

    system = SystemManager()

    response = system.open({
        "topic": "programa_inexistente"
    })

    assert "No conozco" in response