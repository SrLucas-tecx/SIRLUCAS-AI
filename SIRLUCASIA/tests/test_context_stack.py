from app.core.context_stack import ContextStack


def test_push_last_program():

    stack = ContextStack()

    stack.push_program("notepad")

    assert stack.last_program() == "notepad"


def test_pop_program():

    stack = ContextStack()

    stack.push_program("chrome")

    assert stack.pop_program() == "chrome"
    assert stack.last_program() is None


def test_duplicate_program():

    stack = ContextStack()

    stack.push_program("notepad")
    stack.push_program("chrome")
    stack.push_program("notepad")

    assert stack.programs == ["chrome", "notepad"]

def test_push_last_document():

    stack = ContextStack()

    stack.push_document("informe.txt")

    assert stack.last_document() == "informe.txt"


def test_pop_document():

    stack = ContextStack()

    stack.push_document("archivo.pdf")

    assert stack.pop_document() == "archivo.pdf"
    assert stack.last_document() is None


def test_duplicate_document():

    stack = ContextStack()

    stack.push_document("a.txt")
    stack.push_document("b.txt")
    stack.push_document("a.txt")

    assert stack.documents == ["b.txt", "a.txt"]

def test_push_last_search():

    stack = ContextStack()

    stack.push_search("Python")

    assert stack.last_search() == "Python"


def test_pop_search():

    stack = ContextStack()

    stack.push_search("OpenAI")

    assert stack.pop_search() == "OpenAI"
    assert stack.last_search() is None


def test_duplicate_search():

    stack = ContextStack()

    stack.push_search("IA")
    stack.push_search("Python")
    stack.push_search("IA")

    assert stack.searches == ["Python", "IA"]


def test_clear():

    stack = ContextStack()

    stack.push_program("notepad")
    stack.push_document("archivo.txt")
    stack.push_search("Python")

    stack.clear()

    assert stack.programs == []
    assert stack.documents == []
    assert stack.searches == []


def test_empty_stack():

    stack = ContextStack()

    assert stack.last_program() is None
    assert stack.last_document() is None
    assert stack.last_search() is None

    assert stack.pop_program() is None
    assert stack.pop_document() is None
    assert stack.pop_search() is None