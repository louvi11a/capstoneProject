# Generated by Django 5.0.3 on 2024-04-14 07:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0007_intervention_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='healthdetail',
            name='heart_rate',
        ),
    ]
