"""Quotation PDF generation.

Uses WeasyPrint if available. Import is lazy to avoid hard failures in
environments without system dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import html
from typing import Optional

from config.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True)
class PdfResult:
    ok: bool
    pdf_bytes: Optional[bytes] = None
    error: Optional[str] = None


class QuotationPdfService:
    @staticmethod
    def render_html(quotation) -> str:
        # quotation is a SQLAlchemy model; keep rendering simple and escaped.
        qn = html.escape(str(getattr(quotation, "quotation_number", "")))
        status = html.escape(str(getattr(quotation, "status", "")))
        created_at = getattr(quotation, "created_at", None)
        created_str = (
            created_at.strftime("%Y-%m-%d %H:%M")
            if isinstance(created_at, datetime)
            else html.escape(str(created_at))
        )

        client_name = ""
        if getattr(quotation, "client", None) is not None:
            client_obj = quotation.client
            client_name = html.escape(getattr(client_obj, "name", "") or "")

        items_rows = []
        for item in getattr(quotation, "items", []) or []:
            item_name = html.escape(getattr(item, "item_name", "") or "")
            description = html.escape(getattr(item, "description", "") or "")
            quantity = html.escape(str(getattr(item, "quantity", "")))
            unit_price = html.escape(str(getattr(item, "unit_price", "0.00")))
            subtotal = html.escape(str(getattr(item, "subtotal", "0.00")))
            items_rows.append(
                "<tr>"
                f"<td>{item_name}</td>"
                f"<td>{description}</td>"
                f"<td style='text-align:right'>{quantity}</td>"
                f"<td style='text-align:right'>{unit_price}</td>"
                f"<td style='text-align:right'>{subtotal}</td>"
                "</tr>"
            )

        total = html.escape(str(getattr(quotation, "total_amount", "0.00")))
        notes = html.escape(getattr(quotation, "notes", "") or "")
        terms = html.escape(getattr(quotation, "terms_and_conditions", "") or "")

        return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Quotation {qn}</title>
    <style>
      body {{ font-family: sans-serif; font-size: 12px; }}
      h1 {{ font-size: 18px; margin: 0 0 8px 0; }}
      .meta {{ margin: 0 0 12px 0; color: #333; }}
      table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
      th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
      th {{ background: #f5f5f5; text-align: left; }}
      .right {{ text-align: right; }}
      .section {{ margin-top: 14px; }}
    </style>
  </head>
  <body>
    <h1>Quotation {qn}</h1>
    <div class="meta">
      <div><strong>Status:</strong> {status}</div>
      <div><strong>Created:</strong> {created_str}</div>
      {f"<div><strong>Client:</strong> {client_name}</div>" if client_name else ""}
    </div>

    <table>
      <thead>
        <tr>
          <th>Item</th>
          <th>Description</th>
          <th class="right">Qty</th>
          <th class="right">Unit Price</th>
          <th class="right">Subtotal</th>
        </tr>
      </thead>
      <tbody>
        {"".join(items_rows) if items_rows else "<tr><td colspan='5'>No items</td></tr>"}
      </tbody>
      <tfoot>
        <tr>
          <td colspan="4" class="right"><strong>Total</strong></td>
          <td class="right"><strong>{total}</strong></td>
        </tr>
      </tfoot>
    </table>

    {f"<div class='section'><strong>Notes</strong><div>{notes}</div></div>" if notes else ""}
    {f"<div class='section'><strong>Terms</strong><div>{terms}</div></div>" if terms else ""}
  </body>
</html>"""

    @staticmethod
    def render_pdf(quotation) -> PdfResult:
        try:
            from weasyprint import HTML
        except Exception as e:
            return PdfResult(ok=False, error=f"WeasyPrint unavailable: {e}")

        try:
            html_str = QuotationPdfService.render_html(quotation)
            pdf_bytes = HTML(string=html_str).write_pdf()
            return PdfResult(ok=True, pdf_bytes=pdf_bytes)
        except Exception as e:
            logger.error(f"Failed to generate PDF for quotation {getattr(quotation, 'id', '?')}: {e}", exc_info=True)
            return PdfResult(ok=False, error="Failed to generate PDF")
