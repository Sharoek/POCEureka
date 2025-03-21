# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2022 Dimpact
# Generated by Django 3.2.12 on 2022-03-10 22:16

from django.db import migrations

import django_loose_fk.constraints


class Migration(migrations.Migration):

    dependencies = [
        ("besluiten", "0004_auto_20210628_1514"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="besluit",
            name="_besluittype_or__besluittype_url_filled",
        ),
        migrations.RemoveConstraint(
            model_name="besluitinformatieobject",
            name="_informatieobject_or__informatieobject_url_filled",
        ),
        migrations.AddConstraint(
            model_name="besluit",
            constraint=django_loose_fk.constraints.FkOrURLFieldConstraint(
                app_label="besluiten",
                fk_field="_besluittype",
                model_name="besluit",
                url_field="_besluittype_url",
            ),
        ),
        migrations.AddConstraint(
            model_name="besluitinformatieobject",
            constraint=django_loose_fk.constraints.FkOrURLFieldConstraint(
                app_label="besluiten",
                fk_field="_informatieobject",
                model_name="besluitinformatieobject",
                url_field="_informatieobject_url",
            ),
        ),
    ]
