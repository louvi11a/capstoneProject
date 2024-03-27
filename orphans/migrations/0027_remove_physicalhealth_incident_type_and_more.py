# Generated by Django 5.0.1 on 2024-03-25 02:42

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0026_files_related_orphan'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='physicalhealth',
            name='incident_type',
        ),
        migrations.RemoveField(
            model_name='physicalhealth',
            name='orphan',
        ),
        migrations.CreateModel(
            name='BMI',
            fields=[
                ('bmi_ID', models.AutoField(primary_key=True, serialize=False)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('incident_count', models.IntegerField(blank=True, null=True)),
                ('recorded_at', models.DateField(auto_now=True)),
                ('bmi_category', models.CharField(blank=True, choices=[('< 18.5', 'Underweight'), ('18.5 - 24.9', 'Normal Weight'), ('25 - 29.9', 'Overweight'), ('30 or more', 'Obesity')], max_length=20, null=True)),
                ('incident_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orphans.incidenttype')),
                ('orphan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='physical_health', to='orphans.info')),
            ],
            options={
                'db_table': 'orphan_BMI',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='HistoricalBMI',
            fields=[
                ('bmi_ID', models.IntegerField(blank=True, db_index=True)),
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
                'verbose_name': 'historical bmi',
                'verbose_name_plural': 'historical bmis',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.DeleteModel(
            name='HistoricalPhysicalHealth',
        ),
        migrations.DeleteModel(
            name='PhysicalHealth',
        ),
    ]
