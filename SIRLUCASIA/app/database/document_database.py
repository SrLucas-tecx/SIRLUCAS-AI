from app.database.base_database import BaseDatabase


# ==================================================
# DocumentDatabase
# Base de datos de formatos de documentos
# ==================================================

class DocumentDatabase(BaseDatabase):

    def __init__(self):

        super().__init__()

        self.data = {

            # ==============================
            # Texto
            # ==============================

            "txt": ".txt",
            "texto": ".txt",

            # ==============================
            # Word
            # ==============================

            "word": ".docx",
            "doc": ".docx",
            "docx": ".docx",
            "documento word": ".docx",

            # ==============================
            # PDF
            # ==============================

            "pdf": ".pdf",
            "acrobat": ".pdf",

            # ==============================
            # Excel
            # ==============================

            "excel": ".xlsx",
            "xlsx": ".xlsx",
            "hoja de calculo": ".xlsx",
            "hoja de cálculo": ".xlsx",

            # ==============================
            # PowerPoint
            # ==============================

            "powerpoint": ".pptx",
            "power point": ".pptx",
            "ppt": ".pptx",
            "pptx": ".pptx",
            "presentacion": ".pptx",
            "presentación": ".pptx",

            # ==============================
            # Markdown
            # ==============================

            "markdown": ".md",
            "md": ".md",

            # ==============================
            # JSON
            # ==============================

            "json": ".json"

        }

    # ==================================================
    # Buscar formato
    # ==================================================

    def find(self, name):

        if not name:
            return None

        return self.data.get(name.lower().strip())