from app.core.rule_engine import RuleEngine


def test_simple_rule():

    rules = [
        {
            "name": "hola",
            "regex": ["^hola$"],
            "module": "test",
            "command": "hello"
        }
    ]

    engine = RuleEngine(rules)

    result = engine.match("hola")

    assert result["command"] == "hello"