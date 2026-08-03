# Generated manually for the academic project.
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("producers", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="CoffeeReception",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(db_index=True, max_length=30, unique=True)),
                ("received_at", models.DateTimeField(db_index=True)),
                ("coffee_variety", models.CharField(max_length=100)),
                ("process_type", models.CharField(blank=True, max_length=100)),
                ("gross_weight_kg", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("tare_weight_kg", models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
                ("declared_net_weight_kg", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("calculated_net_weight_kg", models.DecimalField(decimal_places=2, editable=False, max_digits=12)),
                ("moisture_percentage", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("status", models.CharField(choices=[("PENDING", "Pendiente"), ("VALIDATED", "Validada"), ("INCONSISTENT", "Con inconsistencia")], db_index=True, default="PENDING", max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("farm", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="receptions", to="producers.farm")),
                ("producer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="receptions", to="producers.producer")),
                ("received_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="coffee_receptions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "recepción de café", "verbose_name_plural": "recepciones de café", "ordering": ["-received_at"]},
        ),
        migrations.CreateModel(
            name="WeightInconsistency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("difference_kg", models.DecimalField(decimal_places=2, max_digits=12)),
                ("description", models.CharField(max_length=300)),
                ("status", models.CharField(choices=[("OPEN", "Abierta"), ("RESOLVED", "Resuelta")], db_index=True, default="OPEN", max_length=20)),
                ("resolution_notes", models.TextField(blank=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("reception", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="weight_inconsistencies", to="receptions.coffeereception")),
                ("resolved_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="resolved_weight_inconsistencies", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "inconsistencia de peso", "verbose_name_plural": "inconsistencias de peso", "ordering": ["-created_at"]},
        ),
        migrations.AddConstraint(model_name="coffeereception", constraint=models.CheckConstraint(condition=models.Q(("gross_weight_kg__gt", models.F("tare_weight_kg"))), name="ck_reception_gross_gt_tare")),
        migrations.AddIndex(model_name="coffeereception", index=models.Index(fields=["producer", "received_at"], name="reception_prod_date_idx")),
        migrations.AddIndex(model_name="coffeereception", index=models.Index(fields=["farm", "received_at"], name="reception_farm_date_idx")),
        migrations.AddIndex(model_name="weightinconsistency", index=models.Index(fields=["status", "created_at"], name="weight_inc_status_idx")),
    ]
