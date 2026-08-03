from datetime import date

from rest_framework import serializers

from apps.reports.services import DateRange


class ReportFilterSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    harvest_year = serializers.IntegerField(required=False, min_value=2000, max_value=2200)

    def validate(self, attrs):
        start_date: date | None = attrs.get("start_date")
        end_date: date | None = attrs.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {"end_date": "La fecha final debe ser posterior o igual a la inicial."}
            )
        return attrs

    def date_range(self) -> DateRange:
        return DateRange(
            start_date=self.validated_data.get("start_date"),
            end_date=self.validated_data.get("end_date"),
        )
