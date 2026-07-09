from app.utils.json_manager import JSONManager


class MemoryManager:

    def __init__(self):

        self.memory = JSONManager.load("data/memory.json")

        if self.memory is None:
            self.memory = {}

    def list_memories(self):

        return self.memory

    def recall(self, key):

        return self.memory.get(key)

    def remember(self, key, value):

        self.memory[key] = value
        JSONManager.save("data/memory.json", self.memory)

    def forget(self, key):

        if key in self.memory:

            del self.memory[key]

            JSONManager.save("data/memory.json", self.memory)

            return True

        return False
    
