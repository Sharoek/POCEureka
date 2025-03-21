# Generated by Django 4.2.11 on 2024-07-04 14:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zgw_consumers", "0012_auto_20210104_1039"),
    ]

    operations = [
        migrations.CreateModel(
            name="KVKConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "profile_service",
                    models.OneToOneField(
                        help_text="Service for API used to retrieve basis profielen.",
                        limit_choices_to={"api_type": "orc"},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="zgw_consumers.service",
                        verbose_name="KvK API Basisprofiel",
                    ),
                ),
                (
                    "search_service",
                    models.OneToOneField(
                        help_text="Service for API used for validation of KvK, RSIN and vestigingsnummer's.",
                        limit_choices_to={"api_type": "orc"},
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="zgw_consumers.service",
                        verbose_name="KvK API Zoeken",
                    ),
                ),
            ],
            options={
                "verbose_name": "KvK configuration",
            },
        ),
    ]
