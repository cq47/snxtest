# Generated by Django 4.1.2 on 2023-01-22 20:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0040_asset_bad_reason_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Position",
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
                ("user_id", models.IntegerField(default=0)),
                ("date", models.DateTimeField(null=True)),
                ("status", models.CharField(default="o", max_length=1)),
                ("iid", models.IntegerField(default=0)),
                ("asset_name", models.CharField(default="", max_length=64)),
                ("side", models.CharField(default="l", max_length=1)),
                ("entry_price", models.FloatField(default=0)),
                ("exit_price", models.FloatField(default=0)),
                ("size", models.FloatField(default=0)),
                ("size_type", models.CharField(default="t", max_length=1)),
                ("pnl", models.FloatField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_current_price",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 23, 20, 23, 27, 676247)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_daily_volume",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 23, 20, 23, 27, 676232)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_is_market_open",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 23, 20, 23, 27, 676243)
            ),
        ),
    ]
