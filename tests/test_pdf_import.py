from server import _normalize_phone, _parse_pdf_text


def test_normalize_extracted_tunisian_phone_number():
    assert _normalize_phone("216) 98 980 066") == "+216 98 980 066"


def test_normalize_tunisian_phone_with_parentheses():
    assert _normalize_phone("+216 (98) 980 066") == "+216 98 980 066"


def test_parse_pdf_text_normalizes_phone_in_header():
    data = _parse_pdf_text(
        "Alex Morgan\nFull-Stack Developer\nTunis | 216) 98 980 066 | alex@example.com"
    )

    assert data["personal"]["phone"] == "+216 98 980 066"