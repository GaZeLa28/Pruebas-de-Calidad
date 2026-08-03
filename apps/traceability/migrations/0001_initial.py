# Generated manually for the academic project.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("lots", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="TraceabilityEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("event_type", models.CharField(choices=[("RECEPTION", "Recepción"), ("LOT_CREATED", "Creación de lote"), ("ASSOCIATION", "Asociación de materia prima"), ("PROCESSING", "Proceso productivo"), ("QUALITY", "Control de calidad"), ("CERTIFICATION", "Certificación"), ("DISPATCH", "Despacho"), ("CORRECTION", "Corrección")], db_index=True, max_length=30)),
                ("occurred_at", models.DateTimeField(db_index=True)),
                ("location", models.CharField(blank=True, max_length=180)),
                ("description", models.TextField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("lot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="traceability_events", to="lots.lot")),
                ("reception", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="traceability_events", to="receptions.coffeereception")),
                ("recorded_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recorded_traceability_events", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "evento de trazabilidad", "verbose_name_plural": "eventos de trazabilidad", "ordering": ["occurred_at", "created_at"]},
        ),
        migrations.AddIndex(model_name="traceabilityevent", index=models.Index(fields=["lot", "occurred_at"], name="trace_lot_date_idx")),
        migrations.AddIndex(model_name="traceabilityevent", index=models.Index(fields=["event_type", "occurred_at"], name="trace_type_date_idx")),
    ]
