from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAuditorOrAdmin
from apps.reports.serializers import ReportFilterSerializer
from apps.reports.services import (
    ExcelReportRenderer,
    PDFReportRenderer,
    ReportDataService,
    ReportExportDataService,
    ReportExportPayload,
)


class BaseReportView(APIView):
    permission_classes = [IsAuditorOrAdmin]

    def get_filters(self, request) -> ReportFilterSerializer:
        serializer = ReportFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer


class ProducerReportView(BaseReportView):
    def get(self, request):
        filters = self.get_filters(request)
        rows = ReportDataService.producer_rows(date_range=filters.date_range())
        return Response({"count": len(rows), "results": rows})


class LotReportView(BaseReportView):
    def get(self, request):
        filters = self.get_filters(request)
        rows = ReportDataService.lot_rows(
            harvest_year=filters.validated_data.get("harvest_year")
        )
        return Response({"count": len(rows), "results": rows})


class ExportReportView(BaseReportView):
    format_name = "xlsx"
    report_type = "producers"

    def get(self, request):
        filters = self.get_filters(request)
        payload = self._build_payload(filters)
        content = self._render(payload)
        return self._build_response(content)

    def _build_payload(self, filters) -> ReportExportPayload:
        return ReportExportDataService.build(
            report_type=self.report_type,
            date_range=filters.date_range(),
            harvest_year=filters.validated_data.get("harvest_year"),
        )

    def _render(self, payload: ReportExportPayload) -> bytes:
        renderer = PDFReportRenderer if self.format_name == "pdf" else ExcelReportRenderer
        return renderer.render(
            title=payload.title,
            headers=payload.headers,
            rows=payload.rows,
        )

    def _build_response(self, content: bytes) -> HttpResponse:
        response = HttpResponse(content, content_type=self._content_type())
        response["Content-Disposition"] = (
            f'attachment; filename="coffeetrace-{self.report_type}.{self.format_name}"'
        )
        return response

    def _content_type(self) -> str:
        if self.format_name == "pdf":
            return "application/pdf"
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
