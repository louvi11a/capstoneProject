# Generated by Django 4.2.3 on 2023-12-29 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0002_info_is_deleted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='info',
            old_name='ethnicity',
            new_name='fathersName',
        ),
        migrations.AddField(
            model_name='info',
            name='homeAddress',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='info',
            name='mothersName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
