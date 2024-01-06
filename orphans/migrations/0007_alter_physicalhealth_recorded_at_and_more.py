# Generated by Django 4.2.3 on 2024-01-05 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orphans', '0006_education_school_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalhealth',
            name='recorded_at',
            field=models.DateField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='HistoricalPhysicalHealth',
            fields=[
                ('healthID', models.IntegerField(blank=True, db_index=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('incident_count', models.IntegerField(blank=True, null=True)),
                ('recorded_at', models.DateField(blank=True, editable=False)),
                ('bmi_category', models.CharField(blank=True, choices=[('< 18.5', 'Underweight'), ('18.5 - 24.9', 'Normal Weight'), ('25 - 29.9', 'Overweight'), ('30 or more', 'Obesity')], max_length=20, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('incident_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='orphans.incidenttype')),
                ('orphan', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='orphans.info')),
            ],
            options={
                'verbose_name': 'historical physical health',
                'verbose_name_plural': 'historical physical healths',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalEducation',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('education_level', models.CharField(choices=[('E', 'Elementary'), ('H', 'High School'), ('C', 'College')], max_length=1)),
                ('school_name', models.CharField(max_length=255)),
                ('current_gpa', models.DecimalField(decimal_places=2, max_digits=3)),
                ('date_recorded', models.DateField(blank=True, editable=False)),
                ('quarter', models.IntegerField(choices=[(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')])),
                ('school_year', models.CharField(max_length=9)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('orphan', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='orphans.info')),
            ],
            options={
                'verbose_name': 'historical education',
                'verbose_name_plural': 'historical educations',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
