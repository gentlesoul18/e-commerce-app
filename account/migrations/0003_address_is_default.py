# Generated by Django 4.1.3 on 2023-02-19 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_rename_apt_address_apartment_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
    ]
