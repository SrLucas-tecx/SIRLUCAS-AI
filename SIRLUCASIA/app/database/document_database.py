from app.database.base_database import BaseDatabase


# ==================================================
# DocumentDatabase
# Base de datos de formatos de documentos
# ==================================================
class DocumentDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            "txt": ".txt",
            "texto": ".txt",

            "word": ".docx",
            "doc": ".docx",
            "docx": ".docx",

            "pdf": ".pdf",

            "excel": ".xlsx",
            "xlsx": ".xlsx",

            "ppt": ".pptx",
            "powerpoint": ".pptx",

            "json": ".json",

            "markdown": ".md",
            "md": ".md"

        }