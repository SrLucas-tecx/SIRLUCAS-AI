from app.core.action_planner import ActionPlanner
from app.core.actions import Action


def test_plan_returns_action():

    planner = ActionPlanner()

    result = planner.plan({
        "module": "system",
        "command": "open",
        "entity": "notepad"
    })

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], Action)


def test_plan_invalid_message():

    planner = ActionPlanner()

    result = planner.plan("hola")

    assert result == []


def test_plan_empty_dict():

    planner = ActionPlanner()

    result = planner.plan({})

    assert len(result) == 1

    action = result[0]

    assert action.module is None
    assert action.command is None
    assert action.entity is None


def test_plan_values():

    planner = ActionPlanner()

    result = planner.plan({
        "module": "knowledge",
        "command": "search",
        "entity": "python"
    })

    action = result[0]

    assert action.module == "knowledge"
    assert action.command == "search"
    assert action.entity == "python"