# Generated by Django 4.1.2 on 2023-01-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0026_remove_asset_ask_price_remove_asset_bid_price_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Asset_Price",
        ),
        migrations.AddField(
            model_name="asset",
            name="close_price",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="asset",
            name="is_market_open",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="asset",
            name="price",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="asset",
            name="volume",
            field=models.FloatField(default=0.0),
        ),
    ]
