from __future__ import annotations

from pathlib import Path

from .builder import CVBuilder
from .config import CONFIG
from .data.cv_data import CV_DATA
from .utils.pdf_utils import count_pdf_pages


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / CONFIG["output_filename"]
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    result = Path(builder.build(output_path))

    pages = count_pdf_pages(result)
    page_str = f"{pages} page(s)" if pages else "unknown pages (pypdf unavailable)"
    print(f"CV generated: {result}")
    print(f"Page count  : {page_str}")


if __name__ == "__main__":
    main()
