from unittest.mock import Mock

import pytest

from bankparser.loader.pdf_loader import PDFLoader


def _mock_pdf_context_manager(pages):
    pdf = Mock()
    pdf.pages = pages

    context_manager = Mock()
    context_manager.__enter__ = Mock(return_value=pdf)
    context_manager.__exit__ = Mock(return_value=False)
    return context_manager


def test_load_extracts_and_joins_text(monkeypatch: pytest.MonkeyPatch) -> None:
    page_one = Mock()
    page_one.extract_text.return_value = "line 1"

    page_two = Mock()
    page_two.extract_text.return_value = "line 2"

    fake_open = Mock(return_value=_mock_pdf_context_manager([page_one, page_two]))
    monkeypatch.setattr("bankparser.loader.pdf_loader.pdfplumber.open", fake_open)

    result = PDFLoader.load("statement.pdf", password="secret")

    assert result == "line 1\nline 2"
    fake_open.assert_called_once_with("statement.pdf", password="secret")


def test_load_skips_empty_page_text(monkeypatch: pytest.MonkeyPatch) -> None:
    page_one = Mock()
    page_one.extract_text.return_value = ""

    page_two = Mock()
    page_two.extract_text.return_value = None

    page_three = Mock()
    page_three.extract_text.return_value = "kept"

    fake_open = Mock(return_value=_mock_pdf_context_manager([page_one, page_two, page_three]))
    monkeypatch.setattr("bankparser.loader.pdf_loader.pdfplumber.open", fake_open)

    result = PDFLoader.load("statement.pdf")

    assert result == "kept"


def test_load_from_scanned_pdf_runs_ocr_for_each_page(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    image_one = object()
    image_two = object()

    page_one = Mock()
    page_one.to_image.return_value = Mock(original=image_one)

    page_two = Mock()
    page_two.to_image.return_value = Mock(original=image_two)

    fake_open = Mock(return_value=_mock_pdf_context_manager([page_one, page_two]))
    fake_ocr = Mock(side_effect=[" first ", "second"])

    monkeypatch.setattr("bankparser.loader.pdf_loader.pdfplumber.open", fake_open)
    monkeypatch.setattr("bankparser.loader.pdf_loader.pytesseract.image_to_string", fake_ocr)

    result = PDFLoader.load_from_scanned_pdf(
        "scanned.pdf",
        password="pw",
        lang="por",
        resolution=200,
    )

    assert result == "first\nsecond"
    fake_open.assert_called_once_with("scanned.pdf", password="pw")
    page_one.to_image.assert_called_once_with(resolution=200)
    page_two.to_image.assert_called_once_with(resolution=200)
    fake_ocr.assert_any_call(image_one, lang="por")
    fake_ocr.assert_any_call(image_two, lang="por")


def test_load_from_scanned_pdf_skips_empty_ocr_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    page_one = Mock()
    page_one.to_image.return_value = Mock(original=object())

    page_two = Mock()
    page_two.to_image.return_value = Mock(original=object())

    fake_open = Mock(return_value=_mock_pdf_context_manager([page_one, page_two]))
    fake_ocr = Mock(side_effect=["   ", "  final text  "])

    monkeypatch.setattr("bankparser.loader.pdf_loader.pdfplumber.open", fake_open)
    monkeypatch.setattr("bankparser.loader.pdf_loader.pytesseract.image_to_string", fake_ocr)

    result = PDFLoader.load_from_scanned_pdf("scanned.pdf")

    assert result == "final text"
