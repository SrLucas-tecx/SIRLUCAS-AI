from app.database.calculator_database import CalculatorDatabase


def test_sum():

    db = CalculatorDatabase()

    assert db.find("+") == "add"


def test_power():

    db = CalculatorDatabase()

    assert db.find("^") == "power"


def test_unknown():

    db = CalculatorDatabase()

    assert db.find("//") is None
    