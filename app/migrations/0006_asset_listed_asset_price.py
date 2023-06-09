# Generated by Django 4.1.2 on 2023-01-05 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_asset_desc_asset_exchange_id_asset_image_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="listed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="asset",
            name="price",
            field=models.FloatField(default=0.0),
        ),
    ]
