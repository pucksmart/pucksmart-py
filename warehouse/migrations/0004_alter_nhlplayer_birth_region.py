# Generated by Django 5.0.2 on 2024-03-27 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0003_nhlplayer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nhlplayer",
            name="birth_region",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]