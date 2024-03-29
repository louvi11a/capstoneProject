# Generated by Django 5.0.1 on 2024-03-04 08:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0013_files_uploaded_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mother_name', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_dob', models.DateField(blank=True, null=True)),
                ('mother_contact', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_address', models.CharField(blank=True, max_length=255, null=True)),
                ('mother_status', models.CharField(blank=True, max_length=255, null=True)),
                ('father_name', models.CharField(blank=True, max_length=255, null=True)),
                ('father_dob', models.DateField(blank=True, null=True)),
                ('father_contact', models.CharField(blank=True, max_length=255, null=True)),
                ('father_occupation', models.CharField(blank=True, max_length=255, null=True)),
                ('father_address', models.CharField(blank=True, max_length=255, null=True)),
                ('father_status', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'family_infos',
            },
        ),
        migrations.RemoveField(
            model_name='info',
            name='fathersName',
        ),
        migrations.RemoveField(
            model_name='info',
            name='homeAddress',
        ),
        migrations.RemoveField(
            model_name='info',
            name='mothersName',
        ),
        migrations.AddField(
            model_name='info',
            name='family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orphans.family'),
        ),
    ]
