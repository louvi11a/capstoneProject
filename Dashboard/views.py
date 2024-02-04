from django.db.models import Avg
from django.db.models import Count
from behavior.models import Notes
from orphans.models import Info, Files
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.core import serializers
from behavior.models import Notes
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse

# def dashboard_view(request):
#     # Query the database to get the sentiment scores and the orphans
#     notes = Notes.objects.all()
#     sentiment_scores = [note.sentiment_score for note in notes]
#     orphans = [str(note.related_orphan) for note in notes]

#     # Serialize the data to JSON
#     sentiment_scores_json = json.dumps(sentiment_scores)
#     orphans_json = json.dumps(orphans)

#     # Pass the data to the template
#     context = {
#         'sentiment_scores': sentiment_scores_json,
#         'orphans': orphans_json,
#     }
#     return render(request, 'Dashboard/Dashboard.html', context)


def dashboard_view(request):
    # Fetch sentiment data from the database
    sentiment_data = Notes.objects.values(
        'sentiment_score').exclude(sentiment_score=None)

    # Prepare data for the pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    positive_count = sentiment_data.filter(sentiment_score__gt=0).count()
    negative_count = sentiment_data.filter(sentiment_score__lt=0).count()
    neutral_count = sentiment_data.filter(sentiment_score=0).count()
    data = [positive_count, negative_count, neutral_count]

    context = {
        'sentiment_labels': labels,
        'sentiment_data': data,
    }

    return render(request, 'Dashboard/Dashboard.html', context)


def files_detail(request, pk):
    file = get_object_or_404(Files, pk=pk)
    return render(request, 'files/detail.html', {'file': file})


class SearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            infos = Info.objects.filter(Q(firstName__icontains=query) | Q(
                middleName__icontains=query) | Q(lastName__icontains=query))
            files = Files.objects.filter(fileName__icontains=query)
            results = []

            # Add URLs for orphan profiles
            for info in infos:
                results.append({
                    'label': f"{info.firstName} {info.middleName} {info.lastName}",
                    'value': request.build_absolute_uri(f'/orphans/profile/{info.orphanID}/')
                })

            # Add a general URL for files
            files_url = request.build_absolute_uri('/files/')
            for file in files:
                results.append({
                    'label': file.fileName,
                    'value': files_url
                })

            return JsonResponse(results, safe=False)
        return JsonResponse({}, status=400)


def sentiment_details(request):
    # Fetch orphans and their notes from the database
    orphans = Info.objects.all()
    notes = Notes.objects.select_related('related_orphan')

    # Prepare data for the orphans and their notes
    orphans_notes = []
    for orphan in orphans:
        orphan_notes = notes.filter(related_orphan=orphan)
        avg_score = orphan_notes.aggregate(Avg('sentiment_score'))[
            'sentiment_score__avg']
        sentiment = 'Neutral'
        if avg_score is not None:
            if avg_score > 0:
                sentiment = 'Positive'
            elif avg_score < 0:
                sentiment = 'Negative'
        orphan_dict = {
            'orphan': orphan.firstName,
            'orphanID': orphan.orphanID,  # Add this line
            'notes': [note.text for note in orphan_notes],
            'score': avg_score,
            'sentiment': sentiment,
            'orphan_picture': orphan.orphan_picture,
            'firstName': orphan.firstName,
            'middleName': orphan.middleName,
            'lastName': orphan.lastName,
        }
        print(orphan_dict)  # Print the dictionary for debugging
        orphans_notes.append(orphan_dict)

    context = {
        'orphans_notes': orphans_notes,
    }

    return render(request, 'Dashboard/sentiment_details.html', context)


def orphanSentiment_detail(request, orphan_id):
    orphan = get_object_or_404(Info, orphanID=orphan_id)
    return render(request, 'Dashboard/orphanSentiment_detail.html', {'orphan': orphan})
