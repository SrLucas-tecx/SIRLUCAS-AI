from app.document.creators.base_creator import BaseCreator


class TxtCreator(BaseCreator):

    def create(self, filepath, content):

        with open(filepath, "w", encoding="utf-8") as file:

            file.write(content)