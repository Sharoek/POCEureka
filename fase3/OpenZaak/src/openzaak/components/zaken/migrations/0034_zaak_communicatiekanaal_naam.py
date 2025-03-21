# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2024 Dimpact
# Generated by Django 4.2.11 on 2024-05-03 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "zaken",
            "0033_remove_relevantezaakrelatie_zaken_relevantezaakrelatie__relevant_zaak_base_url_and__relevant_zaak_re",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="zaak",
            name="communicatiekanaal_naam",
            field=models.CharField(
                blank=True,
                help_text="**EXPERIMENTEEL** De naam van het medium waarlangs de aanleiding om een zaak te starten is ontvangen.",
                max_length=250,
                verbose_name="communicatiekanaal naam",
            ),
        ),
    ]
