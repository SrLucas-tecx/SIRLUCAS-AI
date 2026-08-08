from app.core.calculator_manager import CalculatorManager


def test_calculate_success():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "calculate",
        "topic": "5+5"
    })

    assert result.success is True
    assert result.data == 10
    assert "Resultado" in result.message


def test_calculate_simple_sum():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "calculate",
        "topic": "2 + 2"
    })

    assert result.success is True
    assert result.data == 4


def test_calculate_power():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "calculate",
        "topic": "2^3"
    })

    assert result.success is True
    assert result.data == 8


def test_calculate_too_complex():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "calculate",
        "topic": "+".join(["1"] * 200)
    })

    assert result.success is False
    assert "compleja" in (result.error or "")


def test_calculate_invalid_expression():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "calculate",
        "topic": "5+"
    })

    assert result.success is False
    assert result.error is not None
    assert "No entendí esa operación." == result.message


def test_unknown_command():

    manager = CalculatorManager()

    result = manager.execute({
        "command": "fake"
    })

    assert result.success is False
    assert result.module == "calculator"
    assert result.command == "fake"