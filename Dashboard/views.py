from .forms import AcademicInterventionForm, BehaviorInterventionForm, HealthInterventionForm
from decimal import Decimal
from django.core.cache import cache
from django.db.models import Prefetch

import json
from django.db.models.functions import Concat
from django.db.models import Avg
from django.db.models import Count
from django.forms import CharField
import numpy as np
# from behavior.models import Notes
from orphans.models import BMI, Info, Files, Notes, get_sentiment_data, intervention_behavior_count, HealthDetail, AcademicIntervention, BehaviorIntervention, HealthIntervention
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
from django.db.models import Count, Case, When, Value
from django.shortcuts import render
# Assuming these are your models
from orphans.models import Education, Grade, Info, Subject
from django.db.models import Max
from datetime import date
from django.db import models
from orphans.models import models
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.core import serializers
from django.db.models import Case, When, Value, CharField
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
from datetime import datetime
from django.db.models.functions import ExtractYear, ExtractMonth
# Now you can use
# Set up logging
logger = logging.getLogger(__name__)


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


def overall_behavior_summary(request):
    try:
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
            year_index = years.index(year)

            if score < -0.2:  # Negative threshold
                negative_counts[year_index] += 1
            elif score > 0.2:  # Positive threshold
                positive_counts[year_index] += 1
            else:  # Neutral
                neutral_counts[year_index] += 1

        datasets = [
            {'label': 'Negative', 'data': negative_counts,
                'backgroundColor': 'rgba(255, 88, 132)'},
            {'label': 'Neutral', 'data': neutral_counts,
                'backgroundColor': 'rgba(192, 192, 192)'},
            {'label': 'Positive', 'data': positive_counts,
                'backgroundColor': 'rgba(62, 181, 192)'}
        ]

        histogram_data = {
            'labels': [str(year) for year in years],
            'datasets': datasets,
        }

        return JsonResponse(histogram_data)
    except Exception as e:
        # Return a JSON error message
        return JsonResponse({'error': str(e)}, status=500)


def individual_behavior_summary(request, orphan_id):
    weekly_scores = Notes.objects.filter(
        related_orphan__orphanID=orphan_id
    ).annotate(
        week=ExtractWeek('timestamp')
    ).values(
        'week'
    ).annotate(
        average_score=Avg('sentiment_score')
    ).order_by('week')

    data = [{'week': score['week'], 'average_score': score['average_score']}
            for score in weekly_scores]

    return JsonResponse(data, safe=False)


def overall_health_summary(request):
    cache_key = 'overall_health_data'
    data = cache.get(cache_key)
    if not data:
        try:
            current_year = datetime.now().year
            current_month = datetime.now().month

            # Use an optimized query with prefetching and aggregation
            orphans = Info.objects.all().prefetch_related(
                Prefetch('health_details')
            )
            data = {
                'labels': [],
                'data': []
            }
            for i in range(4):  # Last four months including the current month
                month = (current_month - i - 1) % 12 + 1
                year = current_year if (
                    current_month - i - 1) >= 0 else current_year - 1
                monthly_scores = []

                for orphan in orphans:
                    score = HealthDetail.calculate_monthly_health_score(
                        orphan, month, year)
                    monthly_scores.append(score)

                average_score = sum(monthly_scores) / \
                    len(monthly_scores) if monthly_scores else 0
                # Prepend to reverse order
                data['labels'].insert(0, f"{year}-{month:02d}")
                data['data'].insert(0, average_score)

            # Cache data for 10 minutes
            cache.set(cache_key, data, 600)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse(data)


def individual_health_summary(request, orphan_id):
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Fetch the orphan record with prefetching to optimize related data retrieval
        orphan = Info.objects.prefetch_related(
            'health_details').get(orphanID=orphan_id)

        data = {
            'labels': [],
            'data': []
        }

        # Collect data for the past four months including the current month
        for i in range(4):  # Adjust range as needed for more or fewer months
            month = (current_month - i - 1) % 12 + 1
            year = current_year if (
                current_month - i - 1) >= 0 else current_year - 1
            if month > current_month:  # Handle year transition
                year -= 1

            health_score = HealthDetail.calculate_monthly_health_score(
                orphan, month, year)
            # Prepend to maintain chronological order
            data['labels'].insert(0, f"{year}-{month:02d}")
            data['data'].insert(0, health_score)

        return JsonResponse(data)

    except Info.DoesNotExist:
        return JsonResponse({'error': 'Orphan not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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


def overall_analysis(request):
    cache_key = 'overall_analysis_data'
    context = cache.get(cache_key)

    if not context:
        current_year = datetime.now().year
        current_month = datetime.now().month

        orphans = Info.objects.prefetch_related(
            'notes',  # Assuming 'notes' is related to behavior scoring
            'educations__grades',  # Fetch grades along with educations
        )

        # Initialize your context dictionary
        context = {
            'orphans': orphans,
            'orphan_statuses': {},
            'monthly_health_scores': {},
            'average_physical_wellbeing_score': 0,
            'average_education_score': 0,
            'average_composite_score': 0,
        }

        # Calculate aggregated data
        total_health_score, total_education_score, total_composite_score = Decimal(
            0), Decimal(0), Decimal(0)
        for orphan in orphans:
            health_score = Decimal(HealthDetail.calculate_monthly_health_score(
                orphan, current_month, current_year) or 0)
            education_score = Decimal(
                orphan.calculate_education_score(last_months=4) or 0)
            behavior_score = Decimal(
                orphan.calculate_behavior_score(last_months=4) or 0)

            context['orphan_statuses'][orphan.orphanID] = orphan.calculate_status()
            context['monthly_health_scores'][orphan.orphanID] = health_score

            total_health_score += health_score
            total_education_score += education_score
            total_composite_score += (education_score * Decimal('0.3') +
                                      health_score * Decimal('0.4') +
                                      behavior_score * Decimal('0.3'))

        orphan_count = max(len(orphans), 1)  # Prevent division by zero
        context.update({
            'average_physical_wellbeing_score': (total_health_score / orphan_count),
            'average_education_score': (total_education_score / orphan_count),
            'average_composite_score': (total_composite_score / orphan_count),
        })

        # Cache the computed context
        cache.set(cache_key, context, 3600)  # Cache for 1 hour

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


def overall_bmi_summary(request):
    logger = logging.getLogger(__name__)

    try:
        logger.debug("overall_bmi_summary")

        # Annotate the BMI objects with year and month fields
        annotated_bmi = BMI.objects.annotate(
            year=ExtractYear('recorded_at'),
            month=ExtractMonth('recorded_at')
        )

        # Now, we find the latest entry for each orphan within each year and month
        latest_bmi_entries = annotated_bmi.values(
            'orphan_id', 'year', 'month'
        ).annotate(
            latest_recorded_at=Max('recorded_at')
        ).values_list('latest_recorded_at', flat=True)

        # Filter the BMI entries to only include the latest for each orphan per month
        bmi_data = annotated_bmi.filter(
            recorded_at__in=latest_bmi_entries
        ).values(
            'year', 'month', 'bmi_category'
        ).annotate(
            count=Count('orphan_id', distinct=True)
        ).order_by('year', 'month')

        # Prepare data for the chart
        data = {
            'labels': [],
            'datasets': {
                'Underweight': {'data': [], 'backgroundColor': 'rgba(255, 99, 132, 0.2)'},
                'Normal Weight': {'data': [], 'backgroundColor': 'rgba(54, 162, 235, 0.2)'},
                'Overweight': {'data': [], 'backgroundColor': 'rgba(255, 206, 86, 0.2)'},
                'Obesity': {'data': [], 'backgroundColor': 'rgba(75, 192, 192, 0.2)'},
            }
        }

        # Unique list of year-month combinations
        year_months = sorted(set([(d['year'], d['month']) for d in bmi_data]))
        for year, month in year_months:
            label = f"{year}-{str(month).zfill(2)}"
            data['labels'].append(label)
            for category in data['datasets']:
                count = next((item['count'] for item in bmi_data if item['year'] == year
                              and item['month'] == month and item['bmi_category'] == category), 0)
                data['datasets'][category]['data'].append(count)

        return JsonResponse(data)

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

    current_year = datetime.now().year
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

    # Iterate over orphans instead of educations to aggregate failing grades count per orphan
    orphans = Info.objects.prefetch_related('educations__grades').all()

    context = {

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


def dashboard_behavior_chart(request):
    current_month = datetime.now().month
    orphans_with_average_sentiment = Notes.objects.filter(
        timestamp__month=current_month
    ).values(
        'related_orphan'
    ).annotate(
        average_score=Avg('sentiment_score')
    ).distinct()

    # Initialize counts for each category
    sentiment_counts = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

    # Determine the category based on the average score and increment the counts
    for orphan in orphans_with_average_sentiment:
        average_score = orphan['average_score']
        orphan_id = orphan['related_orphan']
        if average_score > 0.5:
            sentiment_counts['Positive'] += 1
            category = 'Positive'
        elif -0.5 < average_score <= 0.5:
            sentiment_counts['Neutral'] += 1
            category = 'Neutral'
        else:
            sentiment_counts['Negative'] += 1
            category = 'Negative'

        # Log the information
        print(f"Orphan ID: {orphan_id}, Average Score: {
              average_score}, Sentiment Category: {category}")

    data = {
        'labels': ['Negative', 'Neutral', 'Positive'],
        'datasets': [{
            'data': [sentiment_counts['Negative'], sentiment_counts['Neutral'], sentiment_counts['Positive']]
        }]
    }

    return JsonResponse(data)


def intervention_behavior(request):
    current_year = datetime.now().year
    orphan_scores = Notes.objects.values('related_orphan').annotate(
        average_score=Avg('sentiment_score'),
        last_modified=Max('timestamp')  # Fetches the last modification date
    )

    intervention_status_colors = {
        'unresolved': 'danger',  # Red color for unresolved issues
        'pending': 'warning',  # Yellow color for pending issues
        'resolved': 'success',  # Green color for resolved issues
        None: 'info'  # Blue color for no intervention needed
    }

    orphans_with_sentiment = []
    for orphan_score in orphan_scores:
        orphan_id = orphan_score['related_orphan']
        orphan = Info.objects.get(pk=orphan_id)
        average_score = orphan_score['average_score']
        last_modified = orphan_score['last_modified']

        latest_intervention = orphan.interventions.order_by(
            '-last_modified').first()

        if latest_intervention:
            intervention_status = latest_intervention.status
            intervention_plan = latest_intervention.description
        else:
            # Set default values if no intervention exists
            intervention_status = 'unresolved' if average_score < -0.5 else None
            intervention_plan = ''

        intervention_color = intervention_status_colors.get(
            intervention_status, 'info')

        # Determine sentiment category based on the average score
        if average_score > 0.5:
            sentiment_category = 'Meets expectations'
        elif -0.5 <= average_score <= 0.5:
            sentiment_category = 'Needs significant improvement'
        else:
            sentiment_category = 'Needs critical improvement'

        orphans_with_sentiment.append({
            'orphan': orphan,
            'average_score': average_score,
            'sentiment_category': sentiment_category,
            'last_modified': last_modified,
            'intervention_status': intervention_status,
            'intervention_color': intervention_color,
            'intervention_plan': intervention_plan
        })

    def sort_key(x):
        # Define sort priorities
        status_priority = {
            'Needs critical improvement': 1,
            'Needs significant improvement': 2,
            'Meets expectations': 3
        }
        intervention_priority = {
            'unresolved': 1,
            'pending': 2,
            None: 3,
            'resolved': 4
        }
        return (
            status_priority.get(x['sentiment_category'], 99),
            intervention_priority.get(x['intervention_status'], 99)
        )

    orphans_with_sentiment.sort(key=sort_key)

    return render(request, 'Dashboard/chart_behavior.html', {'orphans_with_sentiment': orphans_with_sentiment})


def dashboard_academic_chart(request):
    current_month_start = now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)

    # Aggregate counts by current month and by academic status
    academic_statuses = Grade.objects.annotate(
        month=TruncMonth('education__date_recorded')
    ).filter(
        month=current_month_start
    ).values(
        'education__education_level', 'grade'
    ).annotate(
        count=Count('education__orphan', distinct=True)
    )

    # Initialize the response structure for Chart.js
    chart_data = {
        'labels': ['Meets Expectations', 'Needs Significant Improvement', 'Critical Improvement Needed'],
        'datasets': [{
            'label': 'Number of Orphans',
            'data': [0, 0, 0],  # This will hold counts for each category
            'backgroundColor': [
                'rgba(54, 162, 235, 0.6)',  # Blue
                'rgba(255, 206, 86, 0.6)',  # Yellow
                'rgba(255, 99, 132, 0.6)'   # Red
            ]
        }]
    }

    for status in academic_statuses:
        education_level = status['education__education_level']
        grade = status['grade']
        count = status['count']

        # Define criteria for each category based on the grade and education level
        if (education_level == 'College' and grade <= 2.75) or (education_level in ['Elementary', 'High School'] and grade >= 80):
            chart_data['datasets'][0]['data'][0] += count
        elif (education_level == 'College' and grade == 3.00) or (education_level in ['Elementary', 'High School'] and 70 <= grade < 75):
            chart_data['datasets'][0]['data'][1] += count
        elif (education_level == 'College' and grade >= 4.00) or (education_level in ['Elementary', 'High School'] and grade < 70):
            chart_data['datasets'][0]['data'][2] += count

    return JsonResponse(chart_data)


def intervention_academics(request):
    # Define a dictionary to map intervention statuses to colors
    intervention_status_colors = {
        'unresolved': 'danger',  # Red color for unresolved issues
        'pending': 'warning',  # Yellow color for pending issues
        'resolved': 'success',  # Green color for resolved issues
        None: 'info'  # Blue color for no intervention needed
    }
    print("Dictionary keys:", intervention_status_colors.keys())

    # Fetch all orphans and their latest intervention data
    orphans = Info.objects.prefetch_related(
        'educations__grades', 'academicinterventions').all()
    orphan_educations_status = []

    for orphan in orphans:
        # Order by 'last_modified' to get the latest academic intervention
        latest_intervention = orphan.academicinterventions.order_by(
            '-last_modified').first()
        critical_needed = any(grade.grade < 70 for education in orphan.educations.all(
        ) for grade in education.grades.all())
        significant_needed = any(70 <= grade.grade < 75 for education in orphan.educations.all(
        ) for grade in education.grades.all())

        # Setup intervention status based on latest data or defaults
        if latest_intervention:
            intervention_status = latest_intervention.status
            intervention_color = intervention_status_colors.get(
                intervention_status, 'info')
            remarks = latest_intervention.description
            last_modified = latest_intervention.last_modified
        else:
            # Default values if no intervention exists
            intervention_status = 'unresolved' if critical_needed or significant_needed else None
            intervention_color = intervention_status_colors.get(
                intervention_status, 'info')
            remarks = ''
            last_modified = None

        # Determine the academic status based on intervention needs
        if critical_needed:
            status = 'Critical Improvement Needed'
        elif significant_needed:
            status = 'Needs Significant Improvement'
        else:
            status = 'Meets Expectations'

        # Assuming same color logic for both for simplicity
        status_color = intervention_color

        # Collect data for rendering
        orphan_educations_status.append({
            'orphan': orphan,
            'status': status,
            'status_color': status_color,
            'intervention_status': intervention_status,
            'intervention_color': intervention_color,
            'last_modified': last_modified,
            'remarks': remarks,
        })
        print(f"Final Status: {intervention_status}, Final Color: {
              intervention_color}")

    # Define sort_key function for sorting based on priority

    def sort_key(item):
        # Define priority mapping
        priority_mapping = {
            'Critical Improvement Needed': 1,
            'Needs Significant Improvement': 2,
            'Meets Expectations': 3
        }
        # Resolve to a large number if status is unknown to ensure they appear at the end
        status_priority = priority_mapping.get(item['status'], 99)

        # Secondary sort by intervention status if needed
        intervention_priority_mapping = {
            'unresolved': 1,
            'pending': 2,
            'resolved': 3,
            None: 4
        }
        intervention_priority = intervention_priority_mapping.get(
            item['intervention_status'], 99)

        return (status_priority, intervention_priority)

    # Sorting the list of orphans based on the defined sort key
    orphan_educations_status.sort(key=sort_key)

    context = {
        'orphan_educations_status': orphan_educations_status,
        'orphan_ids': [orphan.orphanID for orphan in Info.objects.all()],
        'orphan_count': Info.objects.count(),
    }
    print(f"Before mapping: status={intervention_status}, available_keys={
          list(intervention_status_colors.keys())}")

    return render(request, 'Dashboard/intervention_academics.html', context)


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


def save_academic_intervention(request, orphan_id):
    if request.method == 'POST':
        form = AcademicInterventionForm(request.POST)
        if form.is_valid():
            orphan = get_object_or_404(Info, pk=orphan_id)
            intervention, created = AcademicIntervention.objects.update_or_create(
                orphan=orphan,
                defaults=form.cleaned_data
            )

            return JsonResponse({'message': 'Intervention saved successfully.'}, status=200)
        else:
            return JsonResponse({'error': form.errors.as_json()}, status=400)

    return JsonResponse({'error': 'Invalid request.'}, status=400)


def intervention_health(request):
    # You can calculate or fetch orphan_count here
    orphan_count = 55
    return render(request, 'Dashboard/intervention_health.html', {'orphan_count': orphan_count})


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
