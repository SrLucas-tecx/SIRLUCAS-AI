from app.core.context_resolver import ContextResolver


class FakeContext:

    def topic(self):
        return "notepad"


class EmptyContext:

    def topic(self):
        return None


def test_replace_reference():

    resolver = ContextResolver()

    data = {
        "topic": "lo"
    }

    result = resolver.resolve(
        data,
        FakeContext()
    )

    assert result["topic"] == "notepad"


def test_replace_eso():

    resolver = ContextResolver()

    data = {
        "topic": "eso"
    }

    result = resolver.resolve(
        data,
        FakeContext()
    )

    assert result["topic"] == "notepad"


def test_keep_normal_topic():

    resolver = ContextResolver()

    data = {
        "topic": "python"
    }

    result = resolver.resolve(
        data,
        FakeContext()
    )

    assert result["topic"] == "python"


def test_no_previous_context():

    resolver = ContextResolver()

    data = {
        "topic": "lo"
    }

    result = resolver.resolve(
        data,
        EmptyContext()
    )

    assert result["topic"] == "lo"


def test_invalid_data():

    resolver = ContextResolver()

    assert resolver.resolve(
        "hola",
        FakeContext()
    ) == "hola"


def test_missing_topic():

    resolver = ContextResolver()

    data = {}

    result = resolver.resolve(
        data,
        FakeContext()
    )

    assert result == {}


def test_all_pronouns():

    resolver = ContextResolver()

    pronouns = [
        "lo",
        "la",
        "eso",
        "este",
        "esta",
        "él",
        "ella"
    ]

    for word in pronouns:

        result = resolver.resolve(
            {"topic": word},
            FakeContext()
        )

        assert result["topic"] == "notepad"