# Generated by Django 5.2 on 2025-04-15 17:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="House",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "house_type",
                    models.CharField(
                        choices=[
                            ("apartment", "Apartment"),
                            ("bedsitter", "Bedsitter"),
                            ("single_room", "Single Room"),
                            ("bungalow", "Bungalow"),
                        ],
                        max_length=20,
                    ),
                ),
                ("number_of_rooms", models.PositiveIntegerField()),
                (
                    "price_per_month",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("location", models.CharField(max_length=255)),
                ("image", models.ImageField(upload_to="house_images/")),
                ("availability_date", models.DateField()),
                ("contact", models.CharField(max_length=100)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="houses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
