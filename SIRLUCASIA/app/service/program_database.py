from app.utils.json_manager import JSONManager


class ProgramDatabase:

    def __init__(self):

        self.path = "data/programs.json"

        self.programs = JSONManager.load(self.path)

        if self.programs is None:
            self.programs = {}

    def get(self, name):

        return self.programs.get(name.lower())

    def save(self, name, path):

        self.programs[name.lower()] = path

        JSONManager.save(
            self.path,
            self.programs
        )

    def all(self):

        return self.programs