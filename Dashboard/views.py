import json
from django.db.models import Avg
from django.db.models import Count
# from behavior.models import Notes
from orphans.models import BMI, Info, Files, Notes, get_sentiment_data, intervention_behavior_count
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.core import serializers
from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Count
from django.db.models.functions import ExtractYear
from django.utils.timezone import now
import logging
import datetime
from django.db.models import Count, Case, When, Value
from django.shortcuts import render
# Assuming these are your models
from orphans.models import Education, Grade, Info, Subject
from django.db.models import Max
from datetime import date
from django.db import models
from orphans.models import models
from django.db.models.functions import TruncMonth
from orphans.models import BMI
from django.db.models import Count

# Set up logging
logger = logging.getLogger(__name__)


def get_orphan_bmi_data(request, orphan_id):
    bmi_records = BMI.objects.filter(orphan=orphan_id).order_by(
        'recorded_at').values('bmi', 'recorded_at')
    data = list(bmi_records)
    return JsonResponse(data, safe=False)


def overall_analysis(request):
    # Assuming calculate_behavior_score, calculate_overall_physical_wellbeing, and calculate_education_score
    # are instance methods that you've already implemented on the Info model
    orphans = Info.objects.all()
    bmi_records = BMI.objects.annotate(month=TruncMonth('recorded_at')).values(
        'month', 'bmi_category').order_by('month').annotate(count=Count('bmi_category'))

    # Organize data for Chart.js
    trend_data = {}
    for record in bmi_records:
        month = record['month'].strftime("%Y-%m")  # Format month as "YYYY-MM"
        category = record['bmi_category']
        count = record['count']

        if month not in trend_data:
            trend_data[month] = {}
        trend_data[month][category] = count

    # Ensure all months have all categories, even if count is 0
    all_categories = ['Underweight', 'Normal Weight', 'Overweight', 'Obese']
    for month in trend_data.keys():
        for category in all_categories:
            if category not in trend_data[month]:
                trend_data[month][category] = 0

                # Prepare lists for chart
    months = list(trend_data.keys())
    categories_data = {category: [trend_data[month].get(
        category, 0) for month in months] for category in all_categories}

    # Calculating averages for all orphans
    average_behavior_score = sum(
        [orphan.calculate_behavior_score() or 0 for orphan in orphans]) / orphans.count()
    average_physical_wellbeing_score = sum(
        [orphan.calculate_overall_physical_wellbeing() or 0 for orphan in orphans]) / orphans.count()
    average_education_score = sum(
        [orphan.calculate_education_score() or 0 for orphan in orphans]) / orphans.count()
    average_composite_score = sum(
        [orphan.calculate_composite_score() or 0 for orphan in orphans]) / orphans.count()

    context = {
        'orphans': orphans,
        'months': json.dumps(months),
        'categories_data': json.dumps(categories_data),
        'average_behavior_score': average_behavior_score,
        'average_physical_wellbeing_score': average_physical_wellbeing_score,
        'average_education_score': average_education_score,
        'average_composite_score': average_composite_score,
    }
    return render(request, 'Dashboard/overall_analysis.html', context)


def sentiment_chart_view(request):
    try:
        positive, negative, neutral = get_sentiment_data()
        sentiment_data = {
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
        }
        return JsonResponse(sentiment_data)
    except Exception as e:
        return JsonResponse({'error': str(e)})


# @login_required
def dashboard_view(request):
    bmi_categories = BMI.objects.values('bmi_category').annotate(
        count=Count('bmi_category')).order_by('bmi_category')
    # Create a dictionary to hold the count for each category
    bmi_data_dict = {category['bmi_category']: category['count']
                     for category in bmi_categories}
    bmi_data = [bmi_data_dict.get(category, 0) for category in [
        'Underweight', 'Normal Weight', 'Overweight', 'Obese']]

    current_year = datetime.datetime.now().year
    orphans = Info.objects.annotate(
        age=Case(
            When(birthDate__isnull=False, then=current_year -
                 ExtractYear('birthDate')),
            default=None,
            output_field=IntegerField(),
        )
    )

    age_ranges = [(0, 10), (11, 20), (21, 30), (31, 40)]
    male_age_data = [0] * len(age_ranges)
    female_age_data = [0] * len(age_ranges)

    for i, (start_age, end_age) in enumerate(age_ranges):
        male_age_data[i] = orphans.filter(
            age__gte=start_age, age__lte=end_age, gender='Male').count()
        female_age_data[i] = orphans.filter(
            age__gte=start_age, age__lte=end_age, gender='Female').count()

    # Fetch sentiment data from the database
    sentiment_data = Notes.objects.values(
        'sentiment_score').exclude(sentiment_score=None)
    # Prepare data for the pie chart
    labels = ['Positive', 'Negative', 'Neutral']
    positive_count = sentiment_data.filter(sentiment_score__gt=0).count()
    negative_count = sentiment_data.filter(sentiment_score__lt=0).count()
    neutral_count = sentiment_data.filter(sentiment_score=0).count()
    data = [positive_count, negative_count, neutral_count]
    male_count = Info.objects.filter(gender='Male').count()
    female_count = Info.objects.filter(gender='Female').count()
    total_orphans = Info.objects.count()
    requires_intervention_behavior = intervention_behavior_count()

    # Prepare initial data structure for academic statuses
    FAILING_GRADE_THRESHOLD = 75

    academic_statuses = {
        'Urgent Academic Support': 0,
        'Partial Support Needed': 0,
        'Stable Academic Standing': 0,
        'Exceptional Academic Standing': 0,
    }

    # Iterate over orphans instead of educations to aggregate failing grades count per orphan
    orphans = Info.objects.prefetch_related('educations__grade_set').all()

    for orphan in orphans:
        urgent_support_needed = False
        partial_support_needed = False
        exceptional_standing = False
        stable_standing = False

        for education in orphan.educations.all():
            failing_grades_count = education.grade_set.filter(
                grade__lte=FAILING_GRADE_THRESHOLD).count()
            highest_grade = education.grade_set.aggregate(Max('grade'))[
                'grade__max'] or 0

            if failing_grades_count >= 3:
                urgent_support_needed = True

            elif 1 <= failing_grades_count <= 2:
                partial_support_needed = True

            if highest_grade >= 91:
                exceptional_standing = True
            elif 76 <= highest_grade <= 90:
                stable_standing = True

        # Update academic status counters based on criteria
        if urgent_support_needed:
            academic_statuses['Urgent Academic Support'] += 1
        elif partial_support_needed:
            academic_statuses['Partial Support Needed'] += 1
        elif exceptional_standing:
            academic_statuses['Exceptional Academic Standing'] += 1
        elif stable_standing:
            academic_statuses['Stable Academic Standing'] += 1
        # Consider adding an else block for orphans that do not fit into any category

    context = {
        'academic_labels': list(academic_statuses.keys()),
        'academic_data': list(academic_statuses.values()),
        'bmi_data': bmi_data,
        'sentiment_labels': labels,
        'sentiment_data': data,
        'male_count': male_count,
        'female_count': female_count,
        'total_orphans': total_orphans,
        'requires_intervention_behavior': requires_intervention_behavior,
        # Add the age distribution data to the existing context
        'age_labels': [f'{start}-{end}' for start, end in age_ranges],
        'male_age_data': male_age_data,
        'female_age_data': female_age_data,

    }

    return render(request, 'Dashboard/Dashboard.html', context)


def chart_behavior(request):
    notes = Notes.objects.all()  # Fetch all notes
    return render(request, 'Dashboard/chart_behavior.html', {'notes': notes})


def chart_bmi(request):
    # This fetches all BMI records and their related orphan info
    bmi_records = BMI.objects.all().select_related('orphan')
    print("bmi records:", bmi_records)

    return render(request, 'Dashboard/chart_bmi.html', {'bmi_records': bmi_records})


def chart_health(request):
    return render(request, 'Dashboard/chart_health.html')


def chart_age(request):
    orphans = Info.objects.all()
    return render(request, 'Dashboard/chart_age.html', {'orphans': orphans})


def chart_academic(request):
    subjects = Subject.objects.all().order_by('name').distinct('name')
    education_records = Education.objects.prefetch_related('grade_set')

    # Combine both context variables into a single dictionary
    context = {
        'education_records': education_records,
        'subjects': subjects,
        'education_level_choices': Education.EDUCATION_LEVEL_CHOICES,
    }

    return render(request, 'Dashboard/chart_academic.html', context)


def intervention_academics(request):
    # You can calculate or fetch orphan_count here
    orphan_count = 55
    return render(request, 'Dashboard/intervention_academics.html', {'orphan_count': orphan_count})


def intervention_health(request):
    # You can calculate or fetch orphan_count here
    orphan_count = 55
    return render(request, 'Dashboard/intervention_health.html', {'orphan_count': orphan_count})


def intervention_behavior(request):
    # You can calculate or fetch orphan_count here
    orphan_count = 55
    return render(request, 'Dashboard/intervention_behavior.html', {'orphan_count': orphan_count})


def files_detail(request, pk):
    file = get_object_or_404(Files, pk=pk)
    return render(request, 'files/detail.html', {'file': file})


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
