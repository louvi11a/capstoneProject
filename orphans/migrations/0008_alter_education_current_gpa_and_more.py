# Generated by Django 4.2.3 on 2024-01-07 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0007_alter_physicalhealth_recorded_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='current_gpa',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='historicaleducation',
            name='current_gpa',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=5, null=True),
        ),
    ]