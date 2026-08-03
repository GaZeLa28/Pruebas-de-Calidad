# Generated manually for the academic project.
import uuid
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("receptions", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Lot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("code", models.CharField(db_index=True, max_length=30, unique=True)),
                ("name", models.CharField(db_index=True, max_length=160)),
                ("harvest_year", models.PositiveSmallIntegerField(db_index=True)),
                ("warehouse_location", models.CharField(blank=True, max_length=160)),
                ("status", models.CharField(choices=[("DRAFT", "Borrador"), ("IN_PROCESS", "En proceso"), ("CERTIFIED", "Certificado"), ("CLOSED", "Cerrado")], db_index=True, default="DRAFT", max_length=20)),
                ("total_weight_kg", models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=14)),
                ("notes", models.TextField(blank=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_lots", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "lote", "verbose_name_plural": "lotes", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="LotQRCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("token", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("generated_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="generated_lot_qr_codes", to=settings.AUTH_USER_MODEL)),
                ("lot", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="qr_code", to="lots.lot")),
            ],
            options={"verbose_name": "código QR de lote", "verbose_name_plural": "códigos QR de lotes"},
        ),
        migrations.CreateModel(
            name="LotReception",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assigned_weight_kg", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("assigned_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lot_reception_assignments", to=settings.AUTH_USER_MODEL)),
                ("lot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reception_links", to="lots.lot")),
                ("reception", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lot_links", to="receptions.coffeereception")),
            ],
            options={"verbose_name": "recepción asociada al lote", "verbose_name_plural": "recepciones asociadas al lote", "ordering": ["created_at"]},
        ),
        migrations.AddField(model_name="lot", name="receptions", field=models.ManyToManyField(related_name="lots", through="lots.LotReception", to="receptions.coffeereception")),
        migrations.AddIndex(model_name="lot", index=models.Index(fields=["harvest_year", "status"], name="lot_harvest_status_idx")),
        migrations.AddConstraint(model_name="lotreception", constraint=models.UniqueConstraint(fields=("lot", "reception"), name="uq_lot_reception")),
        migrations.AddConstraint(model_name="lotreception", constraint=models.CheckConstraint(condition=models.Q(("assigned_weight_kg__gt", 0)), name="ck_lotrec_weight_pos")),
        migrations.AddIndex(model_name="lotreception", index=models.Index(fields=["reception", "lot"], name="lotrec_reception_lot_idx")),
    ]
