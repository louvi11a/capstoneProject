from orphans.models import Info, Files
from django.views import View
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


def files_detail(request, pk):
    file = get_object_or_404(Files, pk=pk)
    return render(request, 'files/detail.html', {'file': file})


class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        print("Received query:", query)  # Print the received query
        if query:
            infos = Info.objects.filter(Q(firstName__icontains=query) | Q(
                middleName__icontains=query) | Q(lastName__icontains=query))
            files = Files.objects.filter(fileName__icontains=query)
            results = list(infos.values('firstName', 'middleName', 'lastName',
                           'orphanID')) + list(files.values('fileName', 'fileID'))
            results = [
                {
                    'label': item['firstName'] + ' ' + item['middleName'] + ' ' + item['lastName'] if 'firstName' in item else item['fileName'],
                    'value': item['firstName'] + ' ' + item['middleName'] + ' ' + item['lastName'] if 'firstName' in item else item['fileName'],
                }
                for item in results
            ]
            print("Infos:", infos)
            print("Files:", files)
            print("Results:", results)
            return JsonResponse(results, safe=False)
        print("No query received")  # Print a message when no query is received
        return JsonResponse({}, status=400)
