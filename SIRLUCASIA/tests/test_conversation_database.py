from app.database.conversation_database import ConversationDatabase


def test_hola():

    db = ConversationDatabase()

    assert db.find("hola") == "¡Hola! ¿En qué puedo ayudarte?"


def test_gracias():

    db = ConversationDatabase()

    assert db.find("gracias") == "De nada."


def test_unknown():

    db = ConversationDatabase()

    assert db.find("xxxxx") is None
    