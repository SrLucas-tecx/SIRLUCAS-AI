from app.core.knowledge_manager import KnowledgeManager


def test_knowledge_load():

    manager = KnowledgeManager()

    assert manager is not None