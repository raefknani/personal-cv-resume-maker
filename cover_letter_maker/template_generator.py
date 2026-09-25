from __future__ import annotations

import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas


class SignatureTemplateGenerator:
    def generate_pdf(self) -> bytes:
        buffer = io.BytesIO()
        canvas = Canvas(buffer, pagesize=A4)
        width, height = A4
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(width / 2, height - 35 * mm, "SIGNATURE TEMPLATE")
        canvas.setFont("Helvetica", 10)
        canvas.drawCentredString(width / 2, height - 45 * mm, "Sign clearly inside the rectangle, then scan or photograph this page.")
        box_w, box_h = 130 * mm, 45 * mm
        x, y = (width - box_w) / 2, height / 2 - box_h / 2
        canvas.setLineWidth(1.5)
        canvas.rect(x, y, box_w, box_h)
        canvas.setFont("Helvetica", 12)
        canvas.drawCentredString(width / 2, y + box_h / 2, "SIGN HERE")
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(width / 2, 30 * mm, "Template version SIG-TPL-1 • Keep all four corners visible")
        canvas.save()
        return buffer.getvalue()