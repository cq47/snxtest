# Generated by Django 4.1.2 on 2023-01-10 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0020_mo_t"),
    ]

    operations = [
        migrations.AddField(
            model_name="asset",
            name="price",
            field=models.FloatField(default=0.0),
        ),
    ]