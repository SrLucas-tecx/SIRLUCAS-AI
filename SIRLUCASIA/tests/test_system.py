from app.service.system_manager import SystemManager


def test_system_exists():

    system = SystemManager()

    assert system.exists("notepad") is True


def test_unknown_program():

    system = SystemManager()

    response = system.open({
        "topic": "programa_inexistente"
    })

    assert response.success is False
    assert "No conozco" in response.message