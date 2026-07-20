from app.database.document_database import DocumentDatabase


def test_word():

    db = DocumentDatabase()

    assert db.find("word") == ".docx"


def test_pdf():

    db = DocumentDatabase()

    assert db.find("pdf") == ".pdf"


def test_excel():

    db = DocumentDatabase()

    assert db.find("excel") == ".xlsx"


def test_json():

    db = DocumentDatabase()

    assert db.find("json") == ".json"


def test_unknown():

    db = DocumentDatabase()

    assert db.find("archivo") is None
    