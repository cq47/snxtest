# Generated by Django 4.1.2 on 2023-01-24 21:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0044_position_initial_bid_price_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="position",
            old_name="initial_bid_price",
            new_name="dollar_size",
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_current_price",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 8, 6, 63614)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_daily_volume",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 8, 6, 63596)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_is_market_open",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 8, 6, 63609)
            ),
        ),
    ]
