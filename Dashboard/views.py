from decimal import Decimal
import json
from django.db.models.functions import Concat
from django.db.models import Avg
from django.db.models import Count
from django.forms import CharField
import numpy as np
# from behavior.models import Notes
from orphans.models import BMI, Info, Files, Notes, get_sentiment_data, intervention_behavior_count, HealthDetail, Intervention
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
from django.core import serializers
from django.db.models import Case, When, Value, CharField
import logging
from django.db.models import F
from django.db.models.functions import ExtractYear, Cast, Concat
from django.db.models.functions import ExtractWeek
from django.db.models.functions import TruncMonth
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from .clustering_logic import perform_clustering
import pandas as pd
from django.db.models import Sum
from . import forms
from django.db.models.functions import ExtractQuarter

# Set up logging
logger = logging.getLogger(__name__)


def save_intervention(request, orphan_id):
    if request.method == 'POST':
        form = forms.InterventionForm(request.POST)
        if form.is_valid():
            try:
                orphan = Info.objects.get(pk=orphan_id)
                intervention_type = 'academic'  # This should be dynamic based on context
                intervention, created = Intervention.objects.get_or_create(
                    orphan=orphan,
                    type=intervention_type,
                    defaults=form.cleaned_data
                )
                if not created:
                    # Update the existing intervention if not newly created
                    for key, value in form.cleaned_data.items():
                        setattr(intervention, key, value)
                    intervention.save()

                return JsonResponse({'message': 'Intervention saved successfully.'}, status=200)
            except Info.DoesNotExist:
                return JsonResponse({'error': 'Orphan not found.'}, status=404)
        else:
            # Or return form errors
            # or you can send this information back in the JsonResponse
            print(form.errors.as_json())
            logger.error(f"Form errors: {form.errors.as_json()}")

            return JsonResponse({'error': 'Form is not valid.'}, status=400)
    return JsonResponse({'error': 'Invalid request.'}, status=400)


def categorize_grades_by_year(grades_with_year):
    categorized_data = {}

    for grade_instance in grades_with_year:
        year = grade_instance.year
        if year not in categorized_data:
            categorized_data[year] = {'Excellent': 0,
                                      'Good': 0, 'Needs Improvement': 0}

        standardized_grade = grade_instance.standardize_grade()
        if standardized_grade >= 90:
            categorized_data[year]['Excellent'] += 1
        elif 75 <= standardized_grade < 90:
            categorized_data[year]['Good'] += 1
        else:
            categorized_data[year]['Needs Improvement'] += 1
    return categorized_data


# used in overall education intervention summary page charts
def overall_gpa_summary(request):
    grades = Grade.objects.annotate(
        year=ExtractYear('education__date_recorded'),
        time_period=Concat(Value('Q'), ExtractQuarter(
            'education__date_recorded'), output_field=CharField())
    ).values('year', 'time_period').annotate(
        average_grade=Avg('grade')
    ).order_by('year', 'time_period')

    return JsonResponse(list(grades), safe=False)


def individual_gpa_summary(request, orphan_id):
    grades = Grade.objects.filter(education__orphan__orphanID=orphan_id).annotate(
        year=ExtractYear('education__date_recorded'),
        time_period=Case(
            When(semester__isnull=False,
                 then=Concat(Value('Semester '), Cast('semester', output_field=CharField()))),
            When(quarter__isnull=False,
                 then=Concat(Value('Quarter '), Cast('quarter', output_field=CharField()))),
            # Optional: Handle cases where neither semester nor quarter is set
            default=Value('N/A'),
            output_field=CharField()
        )
    ).values('year', 'time_period').annotate(
        average_grade=Avg('grade')
    ).order_by('year', 'time_period')

    return JsonResponse(list(grades), safe=False)


def get_color_for_bin(bin_label):
    """
    Determines the color for a given sentiment score range.

    :param bin_label: A string representing the sentiment score range, e.g., "-1.0 to -0.9".
    :return: A string representing the RGBA color for the bin.
    """
    # Extract the start of the range from the bin label
    start_of_range = float(bin_label.split(' to ')[0])

    # Assign colors based on the range
    if start_of_range < -0.5:
        return 'rgba(255, 88, 132)'  # Red for negative sentiment
    elif start_of_range > 0.5:
        return 'rgba(62, 181, 94)'  # Green for positive sentiment
    else:
        return 'rgba(192, 192, 192)'  # Grey for neutral sentiment


def get_orphan_health_data(request, orphan_id):
    try:
        logger.debug("Fetching health data for orphan_id: %s", orphan_id)

        # Assume 'orphan' is the ForeignKey to the Orphan model
        health_data = HealthDetail.objects.filter(orphan_id=orphan_id).annotate(
            month=TruncMonth('date')
        ).values('month').distinct().order_by('month')

        # Preparing the response data
        data = {'labels': [], 'data': []}

        for record in health_data:
            month = record['month'].strftime('%Y-%m')
            # Get all HealthDetail objects for this orphan and month
            details = HealthDetail.objects.filter(
                orphan_id=orphan_id,
                date__month=record['month'].month,
                date__year=record['month'].year,
            )
            # Calculate average health score
            average_score = sum([detail.calculate_health_score()
                                for detail in details]) / len(details) if details else 0

            data['labels'].append(month)
            data['data'].append(average_score)

        # Check if data is empty
        if not data['labels']:
            return JsonResponse({'error': 'No health data found for the given orphan.'}, status=404)

    except Exception as e:
        # This could be improved with more specific exception types and messages
        logger.error(
            "An error occurred while fetching health data: %s", str(e))

        return JsonResponse({'error': 'Server error or invalid request.'}, status=500)

    return JsonResponse(data)


def overall_analysis(request):
    orphans = Info.objects.all()

    # Calculate status for each orphan
    orphan_statuses = {orphan.orphanID: orphan.calculate_status()
                       for orphan in orphans}

    individual_sentiments = {}
    for orphan in orphans:
        # Initialize an empty list for each orphan
        individual_sentiments[orphan.orphanID] = []

        # Get sentiment scores per week for the orphan
        weekly_scores = Notes.objects.filter(
            related_orphan=orphan
        ).annotate(
            week=ExtractWeek('timestamp')
        ).values(
            'week'
        ).annotate(
            average_score=Avg('sentiment_score')
        ).order_by('week')

        for week_score in weekly_scores:
            # Append the weekly average sentiment score to the orphan's list
            individual_sentiments[orphan.orphanID].append({
                'week': week_score['week'],
                'average_score': week_score['average_score']
            })
    # Determine the years present in your data
    years = Notes.objects.annotate(year=ExtractYear('timestamp')).order_by(
        'year').values_list('year', flat=True).distinct()
    years = list(years)

    negative_counts = [0 for _ in years]
    neutral_counts = [0 for _ in years]
    positive_counts = [0 for _ in years]

    # Query to get year, sentiment_score and count distinct orphans
    queryset = Notes.objects.annotate(year=ExtractYear('timestamp')).values(
        'year', 'sentiment_score', 'related_orphan').distinct()

    for note in queryset:
        year = note['year']
        score = note['sentiment_score']

        # Find the index for the year to increment the count
        year_index = years.index(year)

        if score < -0.5:
            negative_counts[year_index] += 1
        elif score > 0.5:
            positive_counts[year_index] += 1
        else:
            neutral_counts[year_index] += 1

    datasets = [
        {'label': 'Negative', 'data': negative_counts,
            'backgroundColor': 'rgba(255, 88, 132)'},
        {'label': 'Neutral', 'data': neutral_counts,
            'backgroundColor': 'rgba(192, 192, 192)'},
        {'label': 'Positive', 'data': positive_counts,
            'backgroundColor': 'rgba(62, 181, 192)'}
    ]

    histogram_data_json = json.dumps({
        # Convert year numbers to strings
        'labels': [str(year) for year in years],
        'datasets': datasets,
    })

    health_details = HealthDetail.objects.annotate(
        month=TruncMonth('date')).order_by('month')

    health_data_by_month = defaultdict(lambda: defaultdict(int))
    for detail in health_details:
        health_score = detail.calculate_health_score()
        month = detail.month.strftime("%Y-%m")

        # Categorize the health score
        if health_score >= 80:
            category = 'Normal'
        elif 50 <= health_score < 80:
            category = 'At-Risk'
        else:
            category = 'Critical'

        health_data_by_month[month][category] += 1

    # Prepare data for Chart.js
    health_trend_data = []
    for month, categories in health_data_by_month.items():
        month_data = {'month': month}
        month_data.update(categories)
        health_trend_data.append(month_data)

    months = sorted(health_data_by_month.keys())
    health_chart_data = {
        'labels': months,
        'datasets': [
            {
                'label': 'Normal',
                'data': [health_data_by_month[month]['Normal'] for month in months],
                'backgroundColor': 'rgba(75, 192, 192)',
            },
            {
                'label': 'At-Risk',
                'data': [health_data_by_month[month]['At-Risk'] for month in months],
                'backgroundColor': 'rgba(255, 206, 86)',
            },
            {
                'label': 'Critical',
                'data': [health_data_by_month[month]['Critical'] for month in months],
                'backgroundColor': 'rgba(255, 99, 132)',
            },
        ],
    }

    bmi_records = BMI.objects.annotate(month=TruncMonth('recorded_at')).values(
        'month', 'bmi_category').order_by('month').annotate(count=Count('bmi_category'))
    trend_data = {}
    for record in bmi_records:
        month = record['month'].strftime("%Y-%m")
        category = record['bmi_category']
        count = record['count']
        if month not in trend_data:
            trend_data[month] = {}
        trend_data[month][category] = count

    all_categories = ['Underweight', 'Normal Weight', 'Overweight', 'Obesity']
    for month in trend_data:
        for category in all_categories:
            if category not in trend_data[month]:
                trend_data[month][category] = 0

    months = list(trend_data.keys())
    categories_data = {category: [trend_data[month].get(
        category, 0) for month in months] for category in all_categories}

    grades_by_semester = Grade.objects.annotate(
        year=ExtractYear('education__date_recorded'),
    ).values('semester', 'year', 'education__orphan__firstName', 'education__orphan__lastName').annotate(
        average_grade=Avg('grade')
    ).order_by('year', 'semester')

    orphan_count = max(orphans.count(), 1)  # Prevent division by zero
    average_behavior_score = sum(
        (orphan.calculate_behavior_score() or 0 for orphan in orphans), 0) / orphan_count
    average_physical_wellbeing_score = sum(
        (orphan.calculate_overall_physical_wellbeing() or 0 for orphan in orphans), 0) / orphan_count
    average_education_score = sum(
        (orphan.calculate_education_score() or 0 for orphan in orphans), 0) / orphan_count
    average_composite_score = sum(
        (orphan.calculate_composite_score() or 0 for orphan in orphans), 0) / orphan_count

    context = {
        'orphans': orphans,
        'orphan_statuses': orphan_statuses,  # Add the status data here

        'health_chart_data_json': json.dumps(health_chart_data),
        'individual_sentiments': json.dumps(individual_sentiments),

        'histogram_data': histogram_data_json,
        'months': json.dumps(months),
        'categories_data': json.dumps(categories_data),
        'average_behavior_score': average_behavior_score,
        'average_physical_wellbeing_score': average_physical_wellbeing_score,
        'average_education_score': average_education_score,
        'average_composite_score': average_composite_score,
        'gpa_data': json.dumps(list(grades_by_semester), default=str),
    }

    return render(request, 'Dashboard/overall_analysis.html', context)


def get_orphan_bmi_data(request, orphan_id):
    logger = logging.getLogger(__name__)
    try:
        logger.debug("Inside get_orphan_bmi_data view")
        bmi_records = BMI.objects.filter(orphan=orphan_id).order_by(
            'recorded_at').values('bmi', 'recorded_at')
        data = list(bmi_records)

        if not data:  # Check if 'data' is empty before accessing
            logger.info("No data available to return.")
            return JsonResponse({'error': 'No BMI data found for the orphan'}, status=404)

        # If data is found, return it
        logger.info(f"Data to be returned: {data}")
        return JsonResponse({'data': data}, safe=False)

    except ObjectDoesNotExist:
        logger.error(f"No orphan found with ID {orphan_id}")
        return JsonResponse({'error': 'Orphan not found'}, status=404)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return JsonResponse({'error': 'Internal Server Error'}, status=500)


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
        logger.error(f"Error generating sentiment data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# @login_required
def dashboard_view(request):
    bmi_categories = BMI.objects.values('bmi_category').annotate(
        count=Count('bmi_category')).order_by('bmi_category')
    # Create a dictionary to hold the count for each category
    bmi_data_dict = {category['bmi_category']: category['count']
                     for category in bmi_categories}
    bmi_data = [bmi_data_dict.get(category, 0) for category in [
        'Underweight', 'Normal Weight', 'Overweight', 'Obesity']]

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
    FAILING_GRADE_THRESHOLD_COLLEGE = 3

    academic_statuses = {
        'Urgent Academic Support': 0,
        'Partial Support Needed': 0,
        'Stable Academic Standing': 0,
        'Exceptional Academic Standing': 0,
    }

    # Iterate over orphans instead of educations to aggregate failing grades count per orphan
    orphans = Info.objects.prefetch_related('educations__grades').all()

    # count_academic_interventions = Info.objects.filter(
    #     Q(education_level='College', educations__grades__grade__lt=3) |
    #     Q(education_level='Elementary', educations__grades__grade__lt=75) |
    #     Q(education_level='High School', educations__grades__grade__lt=75)
    # ).distinct().count()
    count_academic_interventions = 0
    for orphan in orphans:
        urgent_support_needed = False
        partial_support_needed = False
        exceptional_standing = False
        stable_standing = False

        for education in orphan.educations.all():
            # counting of needs intervention
            count_academic_interventions = Info.objects.filter(
                Q(educations__education_level='College', educations__grades__grade__gt=FAILING_GRADE_THRESHOLD_COLLEGE) |
                Q(educations__education_level__in=[
                  'Elementary', 'High School'], educations__grades__grade__lt=FAILING_GRADE_THRESHOLD)
            ).distinct().count()
            print("academic intervention", count_academic_interventions)

            failing_grades_count = education.grades.filter(
                grade__lte=FAILING_GRADE_THRESHOLD).count()
            highest_grade = education.grades.aggregate(Max('grade'))[
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
        'count_academic_interventions': count_academic_interventions,

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
    education_records = Education.objects.prefetch_related('grades')

    # Combine both context variables into a single dictionary
    context = {
        'education_records': education_records,
        'subjects': subjects,
        'education_level_choices': Education.EDUCATION_LEVEL_CHOICES,
    }

    return render(request, 'Dashboard/chart_academic.html', context)


def intervention_academics(request):
    STATUS_COLORS = {
        'resolved': 'success',
        'pending': 'warning',
        'unresolved': 'danger',
    }

    current_year = now().year

    orphan_educations_status = []

    for orphan in Info.objects.all():
        # Aggregate the failing grades
        total_failing_grades = orphan.educations.filter(
            grades__grade__lt=75,
            grades__education__date_recorded__year=current_year
        ).aggregate(
            failing_grades_count=Sum(
                Case(
                    When(grades__grade__lt=75, then=1),
                    output_field=IntegerField(),
                )
            )
        )['failing_grades_count'] or 0

        # Find the latest education record
        latest_education = orphan.educations.order_by('-date_recorded').first()

        # Determine educational status
        if total_failing_grades >= 2:
            status = 'Critical Improvement Needed'
            status_color = 'danger'
        elif total_failing_grades == 1:
            status = 'Needs Significant Improvement'
            status_color = 'warning'
        else:
            status = 'Meets Expectations'
            status_color = 'success'

        # Get the latest academic intervention status and its color
        latest_intervention = orphan.interventions.filter(type='academic').latest(
            'date_created') if orphan.interventions.filter(type='academic').exists() else None
        intervention_status = latest_intervention.status if latest_intervention else None
        intervention_status_color = STATUS_COLORS.get(
            intervention_status, 'secondary')

        orphan_educations_status.append({
            'orphan': orphan,
            'education': latest_education,
            'status': status,
            'status_color': status_color,
            'date_recorded': latest_education.date_recorded if latest_education else None,
            'orphanID': orphan.orphanID,
            'remarks': latest_intervention.description if latest_intervention else None,
            'intervention_status': intervention_status,
            'intervention_status_color': intervention_status_color,
        })

    context = {
        'orphan_educations_status': orphan_educations_status,
        'orphan_ids': [orphan.orphanID for orphan in Info.objects.all()],
        'orphan_count': Info.objects.count(),
    }

    return render(request, 'Dashboard/intervention_academics.html', context)


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
