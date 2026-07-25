from app.database.base_database import BaseDatabase


# ==================================================
# DocumentDatabase
# Base de datos de formatos de documentos
# ==================================================
class DocumentDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

        "docx": ".docx",
        "txt": ".txt",
        "pdf": ".pdf",
        "xlsx": ".xlsx",
        "pptx": ".pptx",
        "json": ".json",
        "md": ".md"
    }