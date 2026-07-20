from app.database.base_database import BaseDatabase
from app.utils.json_manager import JSONManager


class KnowledgeDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        knowledge = JSONManager.load("data/knowledge.json")

        if knowledge is None:
            knowledge = []

        for item in knowledge:

            self.data[item["topic"].lower()] = item["answer"]