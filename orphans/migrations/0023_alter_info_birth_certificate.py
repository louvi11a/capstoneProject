# Generated by Django 5.0.1 on 2024-03-22 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0022_info_birth_certificate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='birth_certificate',
            field=models.FileField(blank=True, null=True, upload_to='birth_certificates/'),
        ),
    ]
