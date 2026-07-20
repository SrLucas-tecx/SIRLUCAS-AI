from app.database.program_database import ProgramDatabase


def test_notepad():

    db = ProgramDatabase()

    assert db.find("notepad") == "notepad.exe"


def test_paint():

    db = ProgramDatabase()

    assert db.find("paint") == "mspaint.exe"


def test_unknown():

    db = ProgramDatabase()

    assert db.find("programa_inexistente") is None
    