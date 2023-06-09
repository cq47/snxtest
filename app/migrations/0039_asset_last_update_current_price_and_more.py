# Generated by Django 4.1.2 on 2023-01-21 20:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0038_order_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="last_update_current_price",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 3, 20, 585290)
            ),
        ),
        migrations.AddField(
            model_name="asset",
            name="last_update_daily_volume",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 3, 20, 585270)
            ),
        ),
        migrations.AddField(
            model_name="asset",
            name="last_update_is_market_open",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 12, 22, 20, 3, 20, 585285)
            ),
        ),
    ]
