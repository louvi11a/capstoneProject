# Generated by Django 4.2.3 on 2024-01-01 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0005_alter_physicalhealth_bmi_category_delete_bmicategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='school_year',
            field=models.CharField(default=-1, max_length=9),
            preserve_default=False,
        ),
    ]
