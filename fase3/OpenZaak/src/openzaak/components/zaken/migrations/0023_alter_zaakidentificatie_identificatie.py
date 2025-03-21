# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2023 Dimpact
# Generated by Django 3.2.16 on 2023-01-09 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0022_auto_20221214_1413"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zaakidentificatie",
            name="identificatie",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="De unieke identificatie van de ZAAK binnen de organisatie die verantwoordelijk is voor de behandeling van de ZAAK.",
                max_length=40,
                verbose_name="identification number",
            ),
        ),
    ]
