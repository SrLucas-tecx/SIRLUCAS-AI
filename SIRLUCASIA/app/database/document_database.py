from app.database.base_database import BaseDatabase


# ==================================================
# DocumentDatabase
# Base de datos de formatos de documentos
# ==================================================
class DocumentDatabase(BaseDatabase):

    def __init__(self):

        self.data = {

        "word": ".docx",
        "docx": ".docx",

        "excel": ".xlsx",
        "xlsx": ".xlsx",

        "powerpoint": ".pptx",
        "pptx": ".pptx",

        "pdf": ".pdf",

        "txt": ".txt",

        "json": ".json",

        "markdown": ".md",
        "md": ".md"
}