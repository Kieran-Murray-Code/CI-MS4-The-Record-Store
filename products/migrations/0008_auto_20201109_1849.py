# Generated by Django 3.1.2 on 2020-11-09 18:49

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_auto_20201109_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tracklist',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), default=list, size=None),
        ),
    ]