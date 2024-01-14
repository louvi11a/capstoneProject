# Generated by Django 4.2.3 on 2024-01-08 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0008_alter_education_current_gpa_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='quarter',
            field=models.IntegerField(blank=True, choices=[(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')], null=True),
        ),
        migrations.AlterField(
            model_name='historicaleducation',
            name='quarter',
            field=models.IntegerField(blank=True, choices=[(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')], null=True),
        ),
    ]
