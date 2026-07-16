import json

from SIRLUCASIA.app.document.creators.base_creator import BaseCreator


class JsonCreator(BaseCreator):

    def create(self, filepath, content):

        with open(filepath, "w", encoding="utf-8") as file:

            json.dump(
                {"content": content},
                file,
                indent=4,
                ensure_ascii=False
            )
            