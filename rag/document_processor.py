import pypdf
from docx import Document

class DocumentProcessor:
    """Handles document loading and processing"""

    @staticmethod
    def load_txt(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def load_pdf(file_path: str) -> str:
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def load_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])

    @classmethod
    def load_document(cls, file_path: str) -> str:
        ext = file_path.lower().split('.')[-1]
        if ext == 'txt':
            return cls.load_txt(file_path)
        elif ext == 'pdf':
            return cls.load_pdf(file_path)
        elif ext == 'docx':
            return cls.load_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
