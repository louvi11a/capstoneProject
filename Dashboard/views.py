from django.shortcuts import render
from django.core import serializers
from behavior.models import Notes
import json


def dashboard_view(request):
    # Query the database to get the sentiment scores and the orphans
    notes = Notes.objects.all()
    sentiment_scores = [note.sentiment_score for note in notes]
    orphans = [str(note.related_orphan) for note in notes]

    # Serialize the data to JSON
    sentiment_scores_json = json.dumps(sentiment_scores)
    orphans_json = json.dumps(orphans)

    # Pass the data to the template
    context = {
        'sentiment_scores': sentiment_scores_json,
        'orphans': orphans_json,
    }
    return render(request, 'Dashboard/Dashboard.html', context)
