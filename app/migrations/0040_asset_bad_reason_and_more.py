# Generated by Django 4.1.2 on 2023-01-21 20:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0039_asset_last_update_current_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="bad_reason",
            field=models.TextField(default=""),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_current_price",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 31, 36, 328179)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_daily_volume",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 31, 36, 328163)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_is_market_open",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 31, 36, 328174)
            ),
        ),
    ]
