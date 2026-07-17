import os
import shutil

from datetime import datetime

from app.database.document_database import DocumentDatabase
from app.document.document_factory import DocumentFactory



# ==================================================
# DocumentManager
# Controla la creación y administración de documentos
# ==================================================

class DocumentManager:

    def __init__(self):

        self.database = DocumentDatabase()

        self.apps = {

        "bloc de notas": "notepad.exe",
        "notepad": "notepad.exe",

        "calculadora": "calc.exe",
        "calc": "calc.exe",

        "explorador": "explorer.exe",

        "paint": "mspaint.exe",

        "vs code": "Code.exe",

        "cmd": "cmd.exe",

        "powershell": "powershell.exe"

    }
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
    
    # ==================================================
    # Renombrar documento
    # ==================================================

    def rename(self, data):
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        
        if not old_name or not new_name:
            return "Faltan nombres para renombrar."
        
        filepath, extension = self.find_document(old_name)
        
        if filepath is None:
            return "No encontré ese documento."
        
        new_path = os.path.join(
        self.path,
        new_name + extension)

        if os.path.exists(new_path):
            return "Ya existe un documento con ese nombre."
        try:
            os.rename(filepath, new_path)
            return (
                f"Documento renombrado de "
                f"'{old_name}{extension}' "
                f"a "
                f"'{new_name}{extension}'."
                )
        except Exception as e:
            return str(e)
        
    # ==================================================
    # Copiar documento
   # ==================================================

    def copy(self, data):
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        
        if not old_name or not new_name:
            return "Faltan nombres para copiar."
        
        filepath, extension = self.find_document(old_name)

        if filepath is None:
          return "No encontré ese documento."
        
        new_path = os.path.join(
        self.path,
        new_name + extension
        )

        if os.path.exists(new_path):
          return "Ya existe un documento con ese nombre."
        
        try:

          shutil.copy2(
              filepath,
              new_path
        )
          return (
            f"Documento copiado de "
            f"'{old_name}{extension}' "
            f"a "
            f"'{new_name}{extension}'."
        )
        except Exception as e:
            return str(e)
    
    # ==================================================
    # Listar documentos
    # ==================================================
    
    def list(self, data):
    
        try:
    
            files = os.listdir(self.path)
    
            if not files:
                return "No hay documentos."
    
            files.sort()
    
            response = (
                f"Documentos encontrados ({len(files)})\n\n"
            )
    
            for file in files:
    
                response += f"• {file}\n"
    
            return response
    
        except Exception as e:
    
            return str(e)
        
    # ==================================================
    # Información del documento
    # ==================================================
    
    def info(self, data):
    
        name = data.get("topic")
    
        if not name:
            return "No especificaste el nombre del documento."
    
        filepath, extension = self.find_document(name)
    
        if filepath is None:
            return "No encontré ese documento."
    
        try:
    
            size = os.path.getsize(filepath)
    
            created = os.path.getctime(filepath)
    
            modified = os.path.getmtime(filepath)
    
            created = datetime.fromtimestamp(created)
    
            modified = datetime.fromtimestamp(modified)
    
            return (
                f"Nombre: {os.path.basename(filepath)}\n"
                f"Formato: {extension}\n"
                f"Tamaño: {size/1024:.2f} KB\n"
                f"Creado: {created.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Modificado: {modified.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Ruta: {filepath}"
            )
    
        except Exception as e:
    
            return str(e)
    # ==================================================
    # Abrir documento
    # ==================================================
    
    import os
import shutil

from datetime import datetime

from app.database.document_database import DocumentDatabase
from app.document.document_factory import DocumentFactory



# ==================================================
# DocumentManager
# Controla la creación y administración de documentos
# ==================================================

class DocumentManager:

    def __init__(self):

        self.database = DocumentDatabase()

        self.apps = {

        "bloc de notas": "notepad.exe",
        "notepad": "notepad.exe",

        "calculadora": "calc.exe",
        "calc": "calc.exe",

        "explorador": "explorer.exe",

        "paint": "mspaint.exe",

        "vs code": "Code.exe",

        "cmd": "cmd.exe",

        "powershell": "powershell.exe"

    }
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
    
    # ==================================================
    # Renombrar documento
    # ==================================================

    def rename(self, data):
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        
        if not old_name or not new_name:
            return "Faltan nombres para renombrar."
        
        filepath, extension = self.find_document(old_name)
        
        if filepath is None:
            return "No encontré ese documento."
        
        new_path = os.path.join(
        self.path,
        new_name + extension)

        if os.path.exists(new_path):
            return "Ya existe un documento con ese nombre."
        try:
            os.rename(filepath, new_path)
            return (
                f"Documento renombrado de "
                f"'{old_name}{extension}' "
                f"a "
                f"'{new_name}{extension}'."
                )
        except Exception as e:
            return str(e)
        
    # ==================================================
    # Copiar documento
   # ==================================================

    def copy(self, data):
        old_name = data.get("old_name")
        new_name = data.get("new_name")
        
        if not old_name or not new_name:
            return "Faltan nombres para copiar."
        
        filepath, extension = self.find_document(old_name)

        if filepath is None:
          return "No encontré ese documento."
        
        new_path = os.path.join(
        self.path,
        new_name + extension
        )

        if os.path.exists(new_path):
          return "Ya existe un documento con ese nombre."
        
        try:

          shutil.copy2(
              filepath,
              new_path
        )
          return (
            f"Documento copiado de "
            f"'{old_name}{extension}' "
            f"a "
            f"'{new_name}{extension}'."
        )
        except Exception as e:
            return str(e)
    
    # ==================================================
    # Listar documentos
    # ==================================================
    
    def list(self, data):
    
        try:
    
            files = os.listdir(self.path)
    
            if not files:
                return "No hay documentos."
    
            files.sort()
    
            response = (
                f"Documentos encontrados ({len(files)})\n\n"
            )
    
            for file in files:
    
                response += f"• {file}\n"
    
            return response
    
        except Exception as e:
    
            return str(e)
        
    # ==================================================
    # Información del documento
    # ==================================================
    
    def info(self, data):
    
        name = data.get("topic")
    
        if not name:
            return "No especificaste el nombre del documento."
    
        filepath, extension = self.find_document(name)
    
        if filepath is None:
            return "No encontré ese documento."
    
        try:
    
            size = os.path.getsize(filepath)
    
            created = os.path.getctime(filepath)
    
            modified = os.path.getmtime(filepath)
    
            created = datetime.fromtimestamp(created)
    
            modified = datetime.fromtimestamp(modified)
    
            return (
                f"Nombre: {os.path.basename(filepath)}\n"
                f"Formato: {extension}\n"
                f"Tamaño: {size/1024:.2f} KB\n"
                f"Creado: {created.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Modificado: {modified.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"Ruta: {filepath}"
            )
    
        except Exception as e:
    
            return str(e)
    # ==================================================
    # Abrir documento
    # ==================================================
    
    def open(self, data):
    
        topic = data.get("topic")
    
        if not topic:
            return "No especificaste qué abrir."
    
        topic = topic.lower()
    
        # ==========================================
        # Intentar abrir aplicación
        # ==========================================
    
        if topic in self.apps:
    
            try:
    
                os.system(f'start "" "{self.apps[topic]}"')
    
                return f"Abriendo {topic}..."
    
            except Exception as e:
    
                return f"No pude abrir {topic}: {e}"
    
        # ==========================================
        # Intentar abrir documento
        # ==========================================
    
        filepath, extension = self.document.find_document(topic)
    
        if filepath is not None:
    
            try:
    
                os.startfile(filepath)
    
                return (
                    f"Abriendo documento "
                    f"'{os.path.basename(filepath)}'."
                )
    
            except Exception as e:
    
                return (
                    f"No pude abrir el documento: {e}"
                )
    
        # ==========================================
        # No encontrado
        # ==========================================
    
        return (
            f"No encontré ninguna aplicación "
            f"ni documento llamado '{topic}'."
        )