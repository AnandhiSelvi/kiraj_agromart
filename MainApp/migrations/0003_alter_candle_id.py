# Generated by Django 4.2 on 2024-06-24 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_candle_volume'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candle',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
