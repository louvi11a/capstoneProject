# Generated by Django 5.0.1 on 2024-03-25 05:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0028_healthdetail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='healthdetail',
            name='others_symptoms',
        ),
    ]
