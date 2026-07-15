from app.database.base_database import BaseDatabase


# ==================================================
# DocumentDatabase
# Base de datos de formatos de documentos
# ==================================================

class DocumentDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            # Texto
            "txt": ".txt",
            "texto": ".txt",

            # Word
            "word": ".docx",
            "doc": ".docx",
            "docx": ".docx",

            # PDF
            "pdf": ".pdf",

            # Excel
            "excel": ".xlsx",
            "xlsx": ".xlsx",

            # PowerPoint
            "powerpoint": ".pptx",
            "ppt": ".pptx",
            "pptx": ".pptx",

            # Markdown
            "markdown": ".md",
            "md": ".md",

            # JSON
            "json": ".json"

        }

    def find(self, name):

        if not name:
            return None

        return self.data.get(name.lower())