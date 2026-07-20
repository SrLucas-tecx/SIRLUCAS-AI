from app.database.knowledge_database import KnowledgeDatabase


def test_python():

    db = KnowledgeDatabase()

    assert db.find("python") is not None


def test_ai():

    db = KnowledgeDatabase()

    assert db.find("inteligencia artificial") is not None


def test_unknown():

    db = KnowledgeDatabase()

    assert db.find("xxxxxxxx") is None