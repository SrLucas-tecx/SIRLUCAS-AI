from app.database.knowledge_database import KnowledgeDatabase


class KnowledgeManager:

    def __init__(self):

        self.database = KnowledgeDatabase()

        print("=" * 50)
        print("[KnowledgeManager]")
        print(f"{len(self.database.list())} conocimientos cargados.")
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
        answer = self.database.find(topic)
        if answer is None:
            return "No conozco ese tema todavía."
        
        return answer