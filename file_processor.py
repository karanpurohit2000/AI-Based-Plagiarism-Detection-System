import PyPDF2
from docx import Document
import pytesseract
from PIL import Image
import re

class FileProcessor:
    ACADEMIC_SECTIONS = [
        r"declaration",
        r"certificate",
        r"acknowledgement",
        r"references",
        r"bibliography",
        r"appendix",
        r"table of contents"
    ]

    def process(self, file_path: str) -> str:
        raw_text = self._process_file(file_path)
        return self._clean_text(raw_text)

    def _process_file(self, file_path: str) -> str:
        if file_path.endswith('.pdf'):
            return self._process_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._process_docx(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return self._process_image(file_path)
        else:
            return self._process_txt(file_path)

    def _clean_text(self, text: str) -> str:
        """Less aggressive cleaning that preserves citations"""
        # Remove section headers but keep content
        text = re.sub(
            r'(?:declaration|certificate|acknowledgement|appendix|table of contents)[:\s]*\n',
            '\n', 
            text, 
            flags=re.IGNORECASE
        )
        
        # Preserve citations and quotes
        text = re.sub(r'\[(\d+)\]', r'[\1]', text)  # Keep citation numbers
        text = re.sub(r'["“”]', '"', text)  # Normalize quotes
        
        return re.sub(r'\s+', ' ', text).strip()
    # Processing methods 
    def _process_pdf(self, path: str) -> str:
        text = []
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return '\n'.join(text)

    def _process_docx(self, path: str) -> str:
        doc = Document(path)
        return '\n'.join([para.text for para in doc.paragraphs])

    def _process_image(self, path: str) -> str:
        return pytesseract.image_to_string(Image.open(path))

    def _process_txt(self, path: str) -> str:
        with open(path, 'r') as f:
            return f.read()