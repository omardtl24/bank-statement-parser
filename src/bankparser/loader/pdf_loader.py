from typing import Optional

import pdfplumber
import pytesseract
from bankparser.loader.base_loader import Loader


class PDFLoader(Loader):
    """Loader for PDF bank statements."""

    def load(
        file_path: str,
        password: Optional[str] = None,
        split_pages: bool = False,
    ) -> str:
        """Extract machine-readable text from a PDF statement.

        Args:
            file_path: Path to the PDF statement.
            password: Optional password for encrypted PDFs.
            split_pages: When ``True``, return one text item per page instead
                of a single concatenated string.

        Returns:
            The extracted text as a string, or a per-page list when
            ``split_pages`` is enabled.

        Raises:
            FileNotFoundError: If ``file_path`` does not exist.
            pdfplumber.utils.exceptions.PDFSyntaxError: If the PDF is invalid
                or malformed.
            Exception: Propagates PDF backend errors (for example, wrong
                password or read failures).
        """
        text_parts = []
        with pdfplumber.open(file_path, password=password) as pdf:
            # Extract text from each page and concatenate the results.
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        if split_pages: return text_parts
        return "\n".join(text_parts).strip()

    def load_from_scanned_pdf(
        file_path: str,
        password: Optional[str] = None,
        lang: str = "eng",
        resolution: int = 300,
    ) -> str:
        """Run OCR over scanned PDF pages and return recognized text.

        Args:
            file_path: Path to the scanned PDF statement.
            password: Optional password for encrypted PDFs.
            lang: Tesseract language code used during OCR.
            resolution: Rasterization DPI used before OCR.

        Returns:
            OCR text from all non-empty pages as a single string.

        Raises:
            FileNotFoundError: If ``file_path`` does not exist.
            pytesseract.pytesseract.TesseractNotFoundError: If the Tesseract
                executable is not installed or not discoverable.
            RuntimeError: If OCR fails while processing page images.
            Exception: Propagates PDF read/rendering errors.
        """
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
