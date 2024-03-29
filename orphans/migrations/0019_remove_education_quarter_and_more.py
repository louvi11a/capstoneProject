# Generated by Django 5.0.1 on 2024-03-14 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0018_remove_grade_semester_remove_grade_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='quarter',
        ),
        migrations.RemoveField(
            model_name='education',
            name='school_year',
        ),
        migrations.RemoveField(
            model_name='education',
            name='semester',
        ),
        migrations.RemoveField(
            model_name='historicaleducation',
            name='quarter',
        ),
        migrations.RemoveField(
            model_name='historicaleducation',
            name='school_year',
        ),
        migrations.RemoveField(
            model_name='historicaleducation',
            name='semester',
        ),
        migrations.AddField(
            model_name='education',
            name='year_level',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='grade',
            name='quarter',
            field=models.IntegerField(blank=True, choices=[(1, 'First Quarter'), (2, 'Second Quarter'), (3, 'Third Quarter'), (4, 'Fourth Quarter')], null=True),
        ),
        migrations.AddField(
            model_name='grade',
            name='semester',
            field=models.IntegerField(blank=True, choices=[(1, 'First Semester'), (2, 'Second Semester')], null=True),
        ),
        migrations.AddField(
            model_name='historicaleducation',
            name='year_level',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
