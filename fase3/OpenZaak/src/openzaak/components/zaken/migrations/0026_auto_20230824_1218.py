# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2023 Dimpact
# Generated by Django 3.2.18 on 2023-08-30 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("zaken", "0025_auto_20230823_1221"),
    ]

    operations = [
        migrations.AddField(
            model_name="status",
            name="gezetdoor",
            field=models.ForeignKey(
                blank=True,
                help_text="De BETROKKENE die in zijn/haar ROL in een ZAAK heeft geregistreerd dat STATUSsen in die ZAAK bereikt zijn.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="statussen",
                to="zaken.rol",
                verbose_name="gezet door",
            ),
        ),
        migrations.AddField(
            model_name="zaakinformatieobject",
            name="status",
            field=models.ForeignKey(
                blank=True,
                help_text="De bij de desbetreffende ZAAK behorende STATUS waarvoor het ZAAK-INFORMATIEOBJECT relevant is (geweest) met het oog op het bereiken van die STATUS en/of de communicatie daarover.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="zaakinformatieobjecten",
                to="zaken.status",
                verbose_name="status",
            ),
        ),
        migrations.AddField(
            model_name="zaakinformatieobject",
            name="vernietigingsdatum",
            field=models.DateTimeField(
                blank=True,
                help_text="De datum waarop het informatieobject uit het zaakdossier verwijderd moet worden.",
                null=True,
                verbose_name="vernietigingsdatum",
            ),
        ),
        migrations.AlterField(
            model_name="zaakinformatieobject",
            name="_objectinformatieobject_url",
            field=models.URLField(
                blank=True,
                help_text="URL of related ObjectInformatieObject object in the other API",
                max_length=1000,
            ),
        ),
    ]
