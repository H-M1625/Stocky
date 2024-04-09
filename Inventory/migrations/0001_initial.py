# Generated by Django 5.0.2 on 2024-02-22 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food', models.CharField(max_length=50)),
                ('price_per_unit', models.FloatField(default=0.0)),
                ('quantity', models.IntegerField(default=0)),
                ('measurement_unit', models.CharField(max_length=50)),
            ],
        ),
    ]
