# Generated by Django 4.2.3 on 2023-12-26 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
