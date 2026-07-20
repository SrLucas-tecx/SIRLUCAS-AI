from app.database.memory_database import MemoryDatabase


def test_add():

    db = MemoryDatabase()

    db.add("nombre", "Juan")

    assert db.find("nombre") == "Juan"


def test_update():

    db = MemoryDatabase()

    db.add("nombre", "Juan")

    db.update("nombre", "Pedro")

    assert db.find("nombre") == "Pedro"


def test_delete():

    db = MemoryDatabase()

    db.add("nombre", "Juan")

    db.delete("nombre")

    assert db.find("nombre") is None


def test_list():

    db = MemoryDatabase()

    db.add("uno", "1")

    db.add("dos", "2")

    lista = db.list()

    assert "uno" in lista
    assert "dos" in lista