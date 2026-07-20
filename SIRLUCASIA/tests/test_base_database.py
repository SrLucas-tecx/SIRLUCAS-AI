from app.database.base_database import BaseDatabase


def test_add():

    db = BaseDatabase()

    db.add("uno", 1)

    assert db.find("uno") == 1


def test_update():

    db = BaseDatabase()

    db.add("uno", 1)

    db.update("uno", 2)

    assert db.find("uno") == 2


def test_delete():

    db = BaseDatabase()

    db.add("uno", 1)

    db.delete("uno")

    assert db.find("uno") is None


def test_list():

    db = BaseDatabase()

    db.add("uno", 1)
    db.add("dos", 2)

    assert len(db.list()) == 2
    