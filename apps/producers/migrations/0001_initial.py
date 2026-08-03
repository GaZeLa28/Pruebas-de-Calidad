# Generated manually for the academic project.
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Producer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("code", models.CharField(db_index=True, max_length=20, unique=True)),
                ("national_id", models.CharField(db_index=True, max_length=30, unique=True)),
                ("full_name", models.CharField(db_index=True, max_length=180)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("address", models.CharField(blank=True, max_length=300)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_producers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "productor", "verbose_name_plural": "productores", "ordering": ["full_name"]},
        ),
        migrations.CreateModel(
            name="Farm",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("code", models.CharField(db_index=True, max_length=25, unique=True)),
                ("name", models.CharField(db_index=True, max_length=160)),
                ("province", models.CharField(max_length=80)),
                ("canton", models.CharField(max_length=80)),
                ("district", models.CharField(max_length=80)),
                ("address", models.CharField(blank=True, max_length=300)),
                ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ("altitude_masl", models.PositiveIntegerField(blank=True, null=True)),
                ("area_hectares", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ("certification", models.CharField(blank=True, max_length=120)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_farms", to=settings.AUTH_USER_MODEL)),
                ("producer", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="farms", to="producers.producer")),
            ],
            options={"verbose_name": "finca", "verbose_name_plural": "fincas", "ordering": ["producer__full_name", "name"]},
        ),
        migrations.AddIndex(model_name="producer", index=models.Index(fields=["is_active", "full_name"], name="producer_active_name_idx")),
        migrations.AddConstraint(model_name="farm", constraint=models.UniqueConstraint(fields=("producer", "name"), name="uq_farm_producer_name")),
        migrations.AddIndex(model_name="farm", index=models.Index(fields=["producer", "is_active"], name="farm_producer_active_idx")),
        migrations.AddIndex(model_name="farm", index=models.Index(fields=["province", "canton", "district"], name="farm_location_idx")),
    ]
