# Generated by Django 4.1.2 on 2023-01-21 00:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0032_alter_asset_daily_volume"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asset",
            name="daily_volume",
            field=models.FloatField(blank=True, default=None),
        ),
    ]
