from typing import Optional

import pdfplumber
import pytesseract
from bankparser.loader.base_loader import Loader


class PDFLoader(Loader):
    """Loader for PDF bank statements."""

    def load(
        self,
        file_path: str,
        password: Optional[str] = None
    ) -> str:
        text_parts = []
        with pdfplumber.open(file_path, password=password) as pdf:
            # Extract text from each page and concatenate the results.
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return "\n".join(text_parts).strip()

    def load_from_scanned_pdf(
        self,
        file_path: str,
        password: Optional[str] = None,
        lang: str = "eng",
        resolution: int = 300,
    ) -> str:
        ocr_parts = []
        with pdfplumber.open(file_path, password=password) as pdf:
            for page in pdf.pages:
                # Render each page to an image and run OCR over the pixels.
                page_image = page.to_image(resolution=resolution).original
                text = pytesseract.image_to_string(page_image, lang=lang)
                cleaned_text = text.strip()
                if cleaned_text:
                    ocr_parts.append(cleaned_text)

        return "\n".join(ocr_parts).strip()
