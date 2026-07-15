import json

from reportlab.pdfgen import canvas
from docx import Document


class DocumentFactory:

    # =====================================
    # TXT
    # =====================================

    @staticmethod
    def create_txt(path, content):

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    # =====================================
    # Markdown
    # =====================================

    @staticmethod
    def create_md(path, content):

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    # =====================================
    # JSON
    # =====================================

    @staticmethod
    def create_json(path, content):

        try:
            data = json.loads(content)

            with open(path, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception:

            with open(path, "w", encoding="utf-8") as file:
                file.write(content)

    # =====================================
    # PDF
    # =====================================

    @staticmethod
    def create_pdf(path, content):

        pdf = canvas.Canvas(path)

        y = 800

        for line in content.split("\n"):

            pdf.drawString(50, y, line)

            y -= 20

        pdf.save()

    # =====================================
    # Word
    # =====================================

    @staticmethod
    def create_docx(path, content):

        doc = Document()

        for line in content.split("\n"):
            doc.add_paragraph(line)

        doc.save(path)

    # =====================================
    # Dispatcher
    # =====================================

    @staticmethod
    def create(extension, path, content):

        creators = {

            ".txt": DocumentFactory.create_txt,
            ".md": DocumentFactory.create_md,
            ".json": DocumentFactory.create_json,
            ".pdf": DocumentFactory.create_pdf,
            ".docx": DocumentFactory.create_docx

        }

        creator = creators.get(extension)

        if creator is None:
            raise ValueError(
                f"Formato no soportado: {extension}"
            )

        creator(path, content)