from app.utils.json_manager import JSONManager


class KnowledgeManager:

    def __init__(self):

        self.knowledge = JSONManager.load(
            "data/knowledge.json"
        )

        if self.knowledge is None:
            self.knowledge = []

        print("=" * 50)
        print("[KnowledgeManager]")
        print(f"{len(self.knowledge)} conocimientos cargados.")
        print("=" * 50)

    def execute(self, data):

        command = data.get("command")

        if command != "search":
            return None

        topic = (
            data.get("topic")
            or data.get("value")
        )

        if topic is None:
            return None

        return self.search(topic)

    def search(self, topic):

        topic = topic.lower()

        for item in self.knowledge:

            if item["topic"] == topic:
                return item["answer"]

        return "No conozco ese tema todavía."