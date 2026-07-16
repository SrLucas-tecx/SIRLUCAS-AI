import os

from app.database.document_database import DocumentDatabase
from app.document.document_factory import DocumentFactory


# ==================================================
# DocumentManager
# Controla la creación y administración de documentos
# ==================================================

class DocumentManager:

    def __init__(self):

        self.database = DocumentDatabase()

        self.path = "documents"

        os.makedirs(self.path, exist_ok=True)

        print("=" * 50)
        print("[DocumentManager]")
        print("Inicializado correctamente.")
        print("=" * 50)

    # ==================================================
    # Router
    # ==================================================

    def execute(self, data):

        command = data.get("command")

        method = getattr(self, command, None)

        if method is None:
            return f"No existe la acción '{command}'."

        return method(data)

    # ==================================================
    # Crear documento
    # ==================================================

    def create(self, data):

        # Nombre
        name = data.get("topic")

        if not name:
            return "No especificaste el nombre del documento."

        # Formato
        format_name = data.get("format")

        extension = self.database.find(format_name)

        if extension is None:
            extension = ".txt"

        # Contenido
        content = data.get("content", "")

        # Ruta completa
        filename = f"{name}{extension}"

        filepath = os.path.join(
            self.path,
            filename
        )

        # Verificar existencia
        if os.path.exists(filepath):
            return f"El documento '{filename}' ya existe."

        # Crear documento
        try:

            DocumentFactory.create(
                extension,
                filepath,
                content
            )

            return f"Documento '{filename}' creado correctamente."

        except Exception as e:

            return f"No pude crear el documento: {e}"

    # ==================================================
    # Leer documento (Sprint 3)
    # ==================================================

    # ==================================================
    # Leer documento
    # ==================================================

    def read(self, data):

        name = data.get("topic")

        if not name:
            return "No especificaste el nombre del documento."

        # Buscar cualquier extensión compatible

        extensions = [
            ".txt",
            ".md",
            ".json",
            ".docx",
            ".pdf"
        ]

        filepath = None

        for ext in extensions:

            path = os.path.join(
                self.path,
                name + ext
            )

            if os.path.exists(path):
                filepath = path
                extension = ext
                break

        if filepath is None:
            return "No encontré ese documento."

        try:

            # TXT
            if extension == ".txt":

                with open(filepath, "r", encoding="utf-8") as file:
                    return file.read()

            # Markdown
            elif extension == ".md":

                with open(filepath, "r", encoding="utf-8") as file:
                    return file.read()

            # JSON
            elif extension == ".json":

                with open(filepath, "r", encoding="utf-8") as file:
                    return file.read()

            # DOCX
            elif extension == ".docx":

                from docx import Document

                doc = Document(filepath)

                texto = []

                for p in doc.paragraphs:
                    texto.append(p.text)

                return "\n".join(texto)

            # PDF

            elif extension == ".pdf":

                return "La lectura de PDF llegará en la siguiente actualización."

        except Exception as e:

            return str(e)

    # ==================================================
    # Escribir documento (Sprint 3)
    # ==================================================

    # ==================================================
    # Escribir en documento
    # ==================================================

    def write(self, data):

        name = data.get("topic")
        content = data.get("content", "")

        if not name:
            return "No especificaste el nombre del documento."

        extensions = [
            ".txt",
            ".md",
            ".json",
            ".docx"
        ]

        filepath = None

        for ext in extensions:

            path = os.path.join(
                self.path,
                name + ext
            )

            if os.path.exists(path):

                filepath = path
                extension = ext
                break

        if filepath is None:
            return "No encontré ese documento."

        try:

            # ==========================
            # TXT
            # ==========================

            if extension == ".txt":

                with open(
                    filepath,
                    "a",
                    encoding="utf-8"
                ) as file:

                    file.write("\n" + content)

            # ==========================
            # Markdown
            # ==========================

            elif extension == ".md":

                with open(
                    filepath,
                    "a",
                    encoding="utf-8"
                ) as file:

                    file.write("\n" + content)

            # ==========================
            # JSON
            # ==========================

            elif extension == ".json":

                return (
                    "Por seguridad todavía no puedo "
                    "modificar archivos JSON."
                )

            # ==========================
            # Word
            # ==========================

            elif extension == ".docx":

                from docx import Document

                doc = Document(filepath)

                doc.add_paragraph(content)

                doc.save(filepath)

            return f"Contenido agregado a '{name}{extension}'."

        except Exception as e:

            return str(e)