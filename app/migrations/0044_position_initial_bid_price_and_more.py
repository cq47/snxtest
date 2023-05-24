# Generated by Django 4.1.2 on 2023-01-24 21:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0043_position_calc_price_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="position",
            name="initial_bid_price",
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_current_price",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 5, 20, 758450)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_daily_volume",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 5, 20, 758430)
            ),
        ),
        migrations.AlterField(
            model_name="asset",
            name="last_update_is_market_open",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 25, 21, 5, 20, 758445)
            ),
        ),
    ]
