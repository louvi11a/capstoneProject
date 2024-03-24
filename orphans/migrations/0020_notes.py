# Generated by Django 5.0.1 on 2024-03-19 01:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orphans', '0019_remove_education_quarter_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notes',
            fields=[
                ('note_id', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('translated_note', models.TextField(blank=True, null=True)),
                ('sentiment_score', models.FloatField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('related_orphan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='orphans.info')),
            ],
        ),
    ]