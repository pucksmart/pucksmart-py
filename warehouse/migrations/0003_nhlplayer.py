# Generated by Django 5.0.2 on 2024-03-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0002_alter_httpsource_e_tag"),
    ]

    operations = [
        migrations.CreateModel(
            name="NhlPlayer",
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
                ("nhl_id", models.IntegerField(unique=True)),
                ("given_name", models.CharField(max_length=64)),
                ("family_name", models.CharField(max_length=64)),
                ("is_active", models.BooleanField(default=False)),
                ("position", models.CharField(max_length=2)),
                ("hall_of_fame", models.BooleanField(default=False)),
                ("birth_date", models.DateField()),
                ("birth_locality", models.CharField(max_length=64)),
                ("birth_region", models.CharField(max_length=64)),
                ("birth_country", models.CharField(max_length=3)),
                ("handedness", models.CharField(max_length=1)),
                ("height", models.IntegerField(blank=True, null=True)),
                ("weight", models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]