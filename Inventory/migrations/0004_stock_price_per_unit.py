# Generated by Django 5.0.2 on 2024-02-22 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Inventory', '0003_rename_price_per_unit_stock_buying_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='price_per_unit',
            field=models.FloatField(default=0.0),
        ),
    ]
