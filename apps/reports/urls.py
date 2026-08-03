from django.urls import path

from apps.reports.api_views import ExportReportView, LotReportView, ProducerReportView


class ProducerExcelExportView(ExportReportView):
    format_name = "xlsx"
    report_type = "producers"


class ProducerPDFExportView(ExportReportView):
    format_name = "pdf"
    report_type = "producers"


class LotExcelExportView(ExportReportView):
    format_name = "xlsx"
    report_type = "lots"


class LotPDFExportView(ExportReportView):
    format_name = "pdf"
    report_type = "lots"


urlpatterns = [
    path("producers/", ProducerReportView.as_view(), name="report-producers"),
    path("lots/", LotReportView.as_view(), name="report-lots"),
    path("producers/export.xlsx", ProducerExcelExportView.as_view(), name="export-producers-xlsx"),
    path("producers/export.pdf", ProducerPDFExportView.as_view(), name="export-producers-pdf"),
    path("lots/export.xlsx", LotExcelExportView.as_view(), name="export-lots-xlsx"),
    path("lots/export.pdf", LotPDFExportView.as_view(), name="export-lots-pdf"),
]
