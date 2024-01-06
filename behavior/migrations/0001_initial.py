# Generated by Django 4.2.3 on 2023-12-26 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orphans', '0001_initial'),
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
            options={
                'db_table': 'OrphanBehavior_notes',
            },
        ),
    ]
