# Generated by Django 4.2.3 on 2023-12-30 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0003_rename_ethnicity_info_fathersname_info_homeaddress_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('education_level', models.CharField(choices=[('E', 'Elementary'), ('H', 'High School'), ('C', 'College')], max_length=1)),
                ('school_name', models.CharField(max_length=255)),
                ('current_gpa', models.DecimalField(decimal_places=2, max_digits=3)),
                ('date_recorded', models.DateField(auto_now_add=True)),
                ('quarter', models.IntegerField(choices=[(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')])),
                ('orphan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='orphans.info')),
            ],
        ),
    ]