from itertools import chain
from django.shortcuts import get_object_or_404, render
from django.core import serializers
from behavior.models import Notes
import json
from django.db.models import Q
from django.shortcuts import render
from orphans.models import Files, Info
from django.http import JsonResponse


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


def search(request):
    query = request.GET.get('q')
    if query:
        results1 = Files.objects.filter(
            Q(fileName__icontains=query) | Q(fileDescription__icontains=query))
        results2 = Info.objects.filter(Q(firstName__icontains=query) | Q(
            middleName__icontains=query) | Q(lastName__icontains=query) | Q(dateAdmitted__icontains=query))
        results = list(chain(results1, results2))
    else:
        results = None
    return render(request, 'search_results.html', {'results': results})


def autocomplete_search(request):
    query = request.GET.get('q')
    if query:
        results1 = Files.objects.filter(
            Q(fileName__icontains=query) | Q(fileDescription__icontains=query))
        results2 = Info.objects.filter(Q(firstName__icontains=query) | Q(
            middleName__icontains=query) | Q(lastName__icontains=query) | Q(dateAdmitted__icontains=query))
        results = list(chain(results1, results2))
        suggestions = [
            {'name': str(result), 'url': result.get_absolute_url()} for result in results]
    else:
        suggestions = []
    return JsonResponse(suggestions, safe=False)


def files_detail(request, pk):
    file = get_object_or_404(Files, pk=pk)
    return render(request, 'files/detail.html', {'file': file})
