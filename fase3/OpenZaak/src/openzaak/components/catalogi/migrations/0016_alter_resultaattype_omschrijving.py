# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2023 Dimpact
# Generated by Django 3.2.18 on 2023-10-16 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogi", "0015_auto_20230908_1438"),
    ]

    operations = [
        migrations.AlterField(
            model_name="resultaattype",
            name="omschrijving",
            field=models.CharField(
                help_text="Omschrijving van de aard van resultaten van het RESULTAATTYPE.",
                max_length=30,
                verbose_name="omschrijving",
            ),
        ),
    ]
