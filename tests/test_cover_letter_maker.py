from pathlib import Path
import io

from PIL import Image, ImageDraw

from cover_letter_maker.models import default_cover_letter_data
from cover_letter_maker.pdf_import import extract_cover_letter
from cover_letter_maker.renderer import CoverLetterRenderer
from cover_letter_maker.signature import SignatureProcessor
from cover_letter_maker.template_generator import SignatureTemplateGenerator


def test_signature_processing_creates_transparent_png():
    image = Image.new("RGB", (320, 120), "white")
    ImageDraw.Draw(image).line((20, 70, 100, 30, 180, 75, 290, 35), fill="black", width=4)
    source = io.BytesIO()
    image.save(source, format="PNG")
    result = SignatureProcessor().process_upload(source.getvalue())
    processed = Image.open(io.BytesIO(result.png_bytes))
    assert processed.mode == "RGBA"
    assert processed.getbbox() is not None


def test_signature_template_is_pdf():
    assert SignatureTemplateGenerator().generate_pdf().startswith(b"%PDF-")


def test_cover_letter_renderer_keeps_text_searchable(tmp_path: Path):
    data = default_cover_letter_data()
    data["personal"]["full_name"] = "Test Applicant"
    data["content"]["typed_name"] = "Test Applicant"
    output = tmp_path / "cover-letter.pdf"
    CoverLetterRenderer().render(data, output_path=output)
    from pypdf import PdfReader
    text = "\n".join(page.extract_text() or "" for page in PdfReader(str(output)).pages)
    assert "Test Applicant" in text


def test_cover_letter_import_rejects_non_pdf():
    try:
        extract_cover_letter(b"not a pdf")
    except ValueError as exc:
        assert "valid PDF" in str(exc)
    else:
        raise AssertionError("invalid PDF should be rejected")