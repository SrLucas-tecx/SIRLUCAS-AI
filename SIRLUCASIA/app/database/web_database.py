from app.database.base_database import BaseDatabase


class WebDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            "google":
                "https://www.google.com/search?q={}",

            "youtube":
                "https://www.youtube.com/results?search_query={}",

            "wikipedia":
                "https://es.wikipedia.org/wiki/{}"

        }