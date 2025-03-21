# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2022 Dimpact
# Generated by Django 3.2.13 on 2022-05-06 14:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalogi", "0010_auto_20210628_0848"),
        ("besluiten", "0005_auto_20220310_2216"),
    ]

    operations = [
        migrations.AlterField(
            model_name="besluit",
            name="_besluittype",
            field=models.ForeignKey(
                blank=True,
                help_text="URL-referentie naar het BESLUITTYPE (in de Catalogi API).",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="catalogi.besluittype",
            ),
        ),
    ]
