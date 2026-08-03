from apps.reports.services import ExcelReportRenderer, PDFReportRenderer


def test_excel_renderer_returns_workbook_bytes():
    content = ExcelReportRenderer.render(
        title="Reporte",
        headers=["Código", "Peso"],
        rows=[["L-1", "100.00"]],
    )
    assert content.startswith(b"PK")


def test_pdf_renderer_returns_pdf_bytes():
    content = PDFReportRenderer.render(
        title="Reporte",
        headers=["Código", "Peso"],
        rows=[["L-1", "100.00"]],
    )
    assert content.startswith(b"%PDF")
