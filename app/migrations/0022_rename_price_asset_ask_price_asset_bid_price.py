# Generated by Django 4.1.2 on 2023-01-10 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0021_asset_price"),
    ]

    operations = [
        migrations.RenameField(
            model_name="asset",
            old_name="price",
            new_name="ask_price",
        ),
        migrations.AddField(
            model_name="asset",
            name="bid_price",
            field=models.FloatField(default=0.0),
        ),
    ]
