import os

from app.database.document_database import DocumentDatabase
from app.factories.document_factory import DocumentFactory


# ==================================================
# DocumentManager
# ==================================================

class DocumentManager:

    def __init__(self):

        self.database = DocumentDatabase()

        self.factory = DocumentFactory()

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

        name = data.get("topic")

        if not name:
            return "No especificaste el nombre."

        format_name = data.get("format")

        extension = self.database.find(format_name)

        if extension is None:
            extension = ".txt"

        content = data.get("content", "")

        filename = f"{name}{extension}"

        filepath = os.path.join(
            self.path,
            filename
        )

        if os.path.exists(filepath):
            return f"El documento '{filename}' ya existe."

        try:

            document = self.factory.create(extension)

            document.save(
                filepath,
                content
            )

            return f"Documento '{filename}' creado correctamente."

        except Exception as e:

            return f"No pude crear el documento: {e}"