# Generated by Django 4.1.2 on 2023-01-21 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0037_order_leverage"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="user_id",
            field=models.IntegerField(default=0),
        ),
    ]
