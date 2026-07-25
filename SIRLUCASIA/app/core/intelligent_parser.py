from app.utils.json_manager import JSONManager

class IntelligentParser:

    def __init__(self):

        self.data = JSONManager.load(
            "data/synonyms.json"
        )