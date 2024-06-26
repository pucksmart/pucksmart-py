# Generated by Django 5.0.2 on 2024-03-17 04:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0006_shift"),
    ]

    operations = [
        migrations.AlterField(
            model_name="team",
            name="franchise",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="stats.franchise",
            ),
        ),
    ]
