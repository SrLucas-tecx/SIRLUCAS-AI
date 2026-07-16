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

        filepath, extension = self.find_document(name)

        if filepath is None:
            return "No encontré ese documento."

        try:

            if extension in [".txt", ".md", ".json"]:

                with open(filepath, "r", encoding="utf-8") as file:
                    return file.read()

            elif extension == ".docx":

                from docx import Document

                doc = Document(filepath)

                return "\n".join(
                    paragraph.text
                    for paragraph in doc.paragraphs
                )

            elif extension == ".pdf":

                return "La lectura de PDF llegará en una próxima versión."

            return "Formato no soportado."

        except Exception as e:

            return str(e)
    # ==================================================
    # Escribir documento (Sprint 3)
    # ==================================================

    # ==================================================
    # Escribir en documento
    # ==================================================

        # ==================================================
    # Escribir documento
    # ==================================================

    def write(self, data):

        name = data.get("topic")
        content = data.get("content", "")

        if not name:
            return "No especificaste el nombre del documento."

        filepath, extension = self.find_document(name)

        if filepath is None:
            return "No encontré ese documento."

        try:

            if extension in [".txt", ".md"]:

                with open(filepath, "a", encoding="utf-8") as file:

                    file.write("\n" + content)

            elif extension == ".docx":

                from docx import Document

                doc = Document(filepath)

                doc.add_paragraph(content)

                doc.save(filepath)

            elif extension == ".json":

                return (
                    "Por seguridad todavía no puedo "
                    "modificar archivos JSON."
                )

            elif extension == ".pdf":

                return (
                    "La edición de PDF estará disponible "
                    "en una próxima versión."
                )

            return f"Contenido agregado a '{os.path.basename(filepath)}'."

        except Exception as e:

            return str(e)
    # ==================================================
    # Buscar documento
    # ==================================================

    def find_document(self, name):

        for file in os.listdir(self.path):

            filename, extension = os.path.splitext(file)

            if filename.lower() == name.lower():

                return os.path.join(self.path, file), extension

        return None, None
    # ==================================================
# Eliminar documento
# ==================================================

def delete(self, data):

    name = data.get("topic")

    if not name:
        return "No especificaste el nombre del documento."

    filepath, extension = self.find_document(name)

    if filepath is None:
        return "No encontré ese documento."

    try:

        os.remove(filepath)

        return f"Documento '{os.path.basename(filepath)}' eliminado correctamente."

    except Exception as e:

        return str(e)
    