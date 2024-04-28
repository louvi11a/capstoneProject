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


def dashboard_view(request):
    requires_intervention_behavior = get_behavior_intervention_count(request)
    requires_intervention_academics = get_academic_intervention_count(request)
    requires_intervention_health = get_health_intervention_count(request)

    bmi_categories = BMI.objects.values('bmi_category').annotate(
        count=Count('bmi_category')).order_by('bmi_category')
    # Create a dictionary to hold the count for each category
    bmi_data_dict = {category['bmi_category']: category['count']
                     for category in bmi_categories}
    bmi_data = [bmi_data_dict.get(category, 0) for category in [
        'Underweight', 'Normal Weight', 'Overweight', 'Obesity']]

    current_year = datetime.now().year

    sentiment_data = Notes.objects.values(
        'sentiment_score').exclude(sentiment_score=None)
    # Prepare data for the pie chart
    male_count = Info.objects.filter(gender='Male').count()
    female_count = Info.objects.filter(gender='Female').count()
    total_orphans = Info.objects.count()

    # Iterate over orphans instead of educations to aggregate failing grades count per orphan
    orphans = Info.objects.prefetch_related('educations__grades').all()

    context = {
        'requires_intervention_behavior': requires_intervention_behavior,
        'requires_intervention_academics': requires_intervention_academics,
        'requires_intervention_health': requires_intervention_health,
        'bmi_data': bmi_data,
        'male_count': male_count,
        'female_count': female_count,
        'total_orphans': total_orphans,
        # Add the age distribution data to the existing context
        # 'age_labels': [f'{start}-{end}' for start, end in age_ranges],``
        # 'male_age_data': male_age_data,
        # 'female_age_data': female_age_data,

    }

    return render(request, 'Dashboard/Dashboard.html', context)


def orphan_status_breakdown(request, orphan_id):
    orphan = Info.objects.get(pk=orphan_id)
    weights = {
        'education': Decimal('0.3'),
        'health': Decimal('0.3'),
        'behavior': Decimal('0.4')
    }
    education_score = Decimal(
        orphan.calculate_education_score(last_months=4) or 0)
    behavior_score = Decimal(
        orphan.calculate_behavior_score(last_months=4) or 0)
    health_score = Decimal(
        HealthDetail.calculate_average_health_score(orphan, months=4) or 0)

    data = {
        'labels': ['Education', 'Health', 'Behavior'],
        'data': [education_score * weights['education'], health_score * weights['health'], behavior_score * weights['behavior']]
    }
    return JsonResponse(data)


def orphan_chart_summary(request, orphan_id):
    # You can pass context variables to the template if needed
    # Fetch the orphan instance using the provided orphanID.
    orphan = get_object_or_404(Info, pk=orphan_id)

    orphan = Info.objects.prefetch_related(
        'physical_health', 'orphan_files').get(orphanID=orphan_id)

    context = {
        'orphan_id': orphan_id,
        'orphan': orphan,

    }
    return render(request, 'Dashboard/orphan_chart_summary.html', context)


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
            default=Value('N/A'),
            output_field=CharField()
        ),
        education_level=F('education__education_level')
    ).values('year', 'time_period', 'education_level').annotate(
        average_grade=Avg('grade')
    ).order_by('year', 'time_period')

    # Normalize the grade data based on education level
    for grade in grades:
        if grade['education_level'] == 'College':
            # Invert college grades so higher is better (e.g., 1 is best, 5 is worst)
            # Assuming grades range from 1 to 5
            grade['average_grade'] = 6 - grade['average_grade']
        # Optionally normalize other grades if needed

    return JsonResponse(list(grades), safe=False)


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
            health_score = Decimal(HealthDetail.calculate_average_health_score(
                orphan) or 0)  # Default to 4 months
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


# def get_academic_intervention_count(request):
#     count = Info.objects.filter(
#         academicinterventions__status='unresolved').count()
#     return count


# def get_health_intervention_count(request):
#     # Count distinct Info objects with unresolved interventions
#     count = Info.objects.filter(
#         healthinterventions__status='unresolved'
#     ).distinct().count()
#     return count


def dashboard_health_chart(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    orphans = Info.objects.all()

    health_categories = {
        'Optimal Health': 0,
        'Good Health': 0,
        'Marginal Health': 0,
        'Poor Health': 0,
    }

    for orphan in orphans:
        score = HealthDetail.calculate_monthly_health_score(
            orphan, current_month, current_year)
        # print(f"Orphan ID {orphan.orphanID}: Score - {score}")  # Add this line

        # Update health_categories based on the calculated score
        # print(health_categories)
        if score >= 95:
            health_categories['Optimal Health'] += 1
        elif score >= 75:
            health_categories['Good Health'] += 1
        elif score >= 50:
            health_categories['Marginal Health'] += 1
        else:
            health_categories['Poor Health'] += 1

   # Format the data for the chart
    data = {
        'labels': list(health_categories.keys()),
        'datasets': [{
            'label': 'Health Status Distribution',
            'data': list(health_categories.values()),
            'backgroundColor': [
                '#4caf50',  # Green for Excellent
                '#ffeb3b',  # Yellow for Good
                '#ff9800',  # Orange for Fair
                '#f44336'  # Red for Poor
            ],
        }]
    }
    # print('data is:', data)
    return JsonResponse(data)


def intervention_health(request):
    current_year = now().year
    current_month = now().month

    health_status_colors = {
        'Optimal Health': 'success',
        'Good Health': 'warning',
        'Marginal Health': 'primary',
        'Poor Health': 'danger',
    }

    intervention_status_colors = {
        'unresolved': 'danger',
        'pending': 'warning',
        'resolved': 'success',
        'none': 'info'  # Assuming 'none' is a valid status in your model choices now
    }

    orphans = Info.objects.all()
    orphans_with_health = []

    for orphan in orphans:
        monthly_health_score = HealthDetail.calculate_monthly_health_score(
            orphan, current_month, current_year)
        health_category = determine_health_category(monthly_health_score)
        latest_intervention = orphan.healthinterventions.order_by(
            '-last_modified').first()

        if not latest_intervention:
            # Create defaults only if no intervention exists
            intervention_status = 'none' if health_category in [
                'Optimal Health', 'Good Health'] else 'unresolved'
            intervention_plan = "Health is optimal or good, no intervention required." if intervention_status == 'none' else "Immediate intervention required due to poor health status."
            latest_intervention = HealthIntervention.objects.create(
                orphan=orphan,
                status=intervention_status,
                description=intervention_plan,
                last_modified=now()
            )
        else:
            # Use existing data to prevent overwriting
            intervention_status = latest_intervention.status
            intervention_plan = latest_intervention.description

        status_color = health_status_colors.get(health_category, 'info')
        intervention_color = intervention_status_colors.get(
            intervention_status, 'info')

        orphans_with_health.append({
            'orphan': orphan,
            'health_score': monthly_health_score,
            'health_category': health_category,
            'status_color': status_color,
            'last_modified': latest_intervention.last_modified,
            'intervention_status': intervention_status,
            'intervention_color': intervention_color,
            'intervention_plan': intervention_plan,
        })

    orphans_with_health.sort(key=lambda x: (
        {'Poor Health': 1, 'Marginal Health': 2, 'Good Health': 3,
            'Optimal Health': 4}.get(x['health_category'], 99),
        {'unresolved': 1, 'pending': 2, 'resolved': 3,
            'none': 4}.get(x['intervention_status'], 99)
    ))

    return render(request, 'Dashboard/intervention_health.html', {'orphans_with_health': orphans_with_health})


def determine_health_category(score):
    if score >= 95:
        return 'Optimal Health'
    elif 75 <= score < 95:
        return 'Good Health'
    elif 50 <= score < 75:
        return 'Marginal Health'
    else:
        return 'Poor Health'


def save_health_intervention(request, orphan_id):
    if request.method == 'POST':
        form = HealthInterventionForm(request.POST)
        if form.is_valid():
            orphan = get_object_or_404(Info, pk=orphan_id)
            # Update or create health intervention for the orphan
            intervention, created = HealthIntervention.objects.update_or_create(
                orphan=orphan,
                defaults=form.cleaned_data
            )

            # Respond with a success message
            return JsonResponse({'message': 'Health intervention saved successfully.'}, status=200)
        else:
            # Return form validation errors
            return JsonResponse({'error': form.errors.as_json()}, status=400)

    # Handle incorrect request methods
    return JsonResponse({'error': 'Invalid request.'}, status=400)


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
        # print(f"Orphan ID: {orphan_id}, Average Score: {
        #       average_score}, Sentiment Category: {category}")

    data = {
        'labels': ['Negative', 'Neutral', 'Positive'],
        'datasets': [{
            'data': [sentiment_counts['Negative'], sentiment_counts['Neutral'], sentiment_counts['Positive']]
        }]
    }

    return JsonResponse(data)


def intervention_behavior(request):
    current_year = now().year

    # Fetch scores and calculate averages and latest modifications
    orphan_scores = Notes.objects.values('related_orphan').annotate(
        average_score=Avg('sentiment_score'),
        last_modified=Max('timestamp')
    )

    # Color mappings for sentiment and intervention statuses
    sentiment_status_colors = {
        'Needs critical improvement': 'danger',
        'Needs improvement': 'warning',
        'Meets expectations': 'success',
    }
    intervention_status_colors = {
        'unresolved': 'danger',
        'pending': 'warning',
        'resolved': 'success',
        'none': 'info'
    }

    orphans_with_sentiment = []
    for orphan_score in orphan_scores:
        orphan_id = orphan_score['related_orphan']
        orphan = Info.objects.get(pk=orphan_id)
        average_score = orphan_score['average_score']
        last_modified = orphan_score['last_modified']

        latest_intervention = orphan.behaviorinterventions.order_by(
            '-last_modified').first()

        sentiment_category = determine_sentiment_category(average_score)
        if latest_intervention:
            intervention_status = latest_intervention.status
        else:
            intervention_status = determine_intervention_status(average_score)
            intervention_plan = determine_intervention_plan_behavior(
                average_score)
            latest_intervention = BehaviorIntervention.objects.create(
                orphan=orphan,
                status=intervention_status,
                description=intervention_plan,
                last_modified=now()
            )

        status_color = sentiment_status_colors.get(sentiment_category, 'info')
        intervention_color = intervention_status_colors.get(
            intervention_status, 'info')

        orphans_with_sentiment.append({
            'orphan': orphan,
            'average_score': average_score,
            'status_color': status_color,
            'sentiment_category': sentiment_category,
            'last_modified': last_modified,
            'intervention_status': intervention_status,
            'intervention_color': intervention_color,
            'intervention_plan': latest_intervention.description
        })

    orphans_with_sentiment.sort(key=lambda x: (
        {'Needs critical improvement': 1, 'Needs improvement': 2,
            'Meets expectations': 3}.get(x['sentiment_category'], 99),
        {'unresolved': 1, 'pending': 2, 'resolved': 4, 'none': 3}.get(
            x['intervention_status'], 99)
    ))

    return render(request, 'Dashboard/intervention_behavior.html', {'orphans_with_sentiment': orphans_with_sentiment})


def determine_sentiment_category(average_score):
    if average_score > 0.5:
        return 'Meets expectations'
    elif -0.5 <= average_score <= 0.5:
        return 'Needs improvement'
    else:
        return 'Needs critical improvement'


def determine_intervention_status(average_score):
    if average_score > 0.5:
        return None
    elif -0.5 <= average_score <= 0.5:
        return 'unresolved'
    else:
        return 'pending'


def determine_intervention_plan_behavior(average_score):
    if average_score > 0.5:
        return "Orphan meets the expectations. No intervention needed."
    elif -0.5 <= average_score <= 0.5:
        return "Orphan needs improvements. Pending review."
    else:
        return "Critical improvements required. Immediate action needed."


def save_behavior_intervention(request, orphan_id):
    if request.method == 'POST':
        form = BehaviorInterventionForm(request.POST)
        if form.is_valid():
            orphan = get_object_or_404(Info, pk=orphan_id)
            intervention, created = BehaviorIntervention.objects.update_or_create(
                orphan=orphan,
                defaults=form.cleaned_data
            )

            return JsonResponse({'message': 'Intervention saved successfully.'}, status=200)
        else:
            return JsonResponse({'error': form.errors.as_json()}, status=400)

    return JsonResponse({'error': 'Invalid request.'}, status=400)


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

            if score > 0.5:  # Adjusted Positive threshold
                positive_counts[year_index] += 1
            elif -0.5 < score <= 0.5:  # Adjusted Neutral threshold
                neutral_counts[year_index] += 1
            else:  # Adjusted Negative threshold
                negative_counts[year_index] += 1

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


def dashboard_academic_chart(request):
    current_month_start = now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)

    chart_data = {
        'labels': ['Meets Expectations', 'Needs Improvement', 'Critical Improvement Needed'],
        'datasets': [{
            'label': 'Number of Orphans',
            'data': [0, 0, 0],
            'backgroundColor': [
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(255, 99, 132, 0.6)'
            ]
        }]
    }

    education_levels = ['College', 'Elementary', 'High School']

    for level in education_levels:
        failing_threshold = 3.0 if level == 'College' else 75

        # Aggregate all grades for this month and year by orphan
        grades = Grade.objects.filter(
            education__education_level=level,
            education__date_recorded__month=current_month_start.month,
            education__date_recorded__year=current_month_start.year
        ).values('education__orphan').annotate(
            total_grades=Count('id'),
            failing_grades=Count('id', filter=Q(grade__gte=failing_threshold))
        )

        orphan_status_counts = {
            'Meeting': 0,
            'Significant': 0,
            'Critical': 0
        }

        # Print the count of grades and the aggregation results
        print(f"Processing {level}: Total graded entries: {grades.count()}")
        for grade in grades:
            print(f"Orphan ID {grade['education__orphan']} - Total Grades: {
                  grade['total_grades']}, Failing Grades: {grade['failing_grades']}")

            if grade['failing_grades'] == 0:
                orphan_status_counts['Meeting'] += 1
            elif grade['failing_grades'] == 1:
                orphan_status_counts['Significant'] += 1
            elif grade['failing_grades'] > 1:
                orphan_status_counts['Critical'] += 1

        print(f"{level} - Meeting: {orphan_status_counts['Meeting']}, Significant: {
              orphan_status_counts['Significant']}, Critical: {orphan_status_counts['Critical']}")

        chart_data['datasets'][0]['data'][0] += orphan_status_counts['Meeting']
        chart_data['datasets'][0]['data'][1] += orphan_status_counts['Significant']
        chart_data['datasets'][0]['data'][2] += orphan_status_counts['Critical']

    print('Educational chart data is', chart_data)
    return JsonResponse(chart_data)


def intervention_academics(request):

    # Color mappings
    academic_status_colors = {
        'Critical Improvement Needed': 'danger',
        'Needs Improvement': 'warning',
        'Meets Expectations': 'success',
    }
    intervention_status_colors = {
        'unresolved': 'danger',
        'pending': 'warning',
        'resolved': 'success',
        'none': 'info'  # Ensuring 'none' is treated as a standard status
    }

    # Fetch all orphans and their latest academic intervention data

    current_year = now().year
    orphans = Info.objects.prefetch_related(
        'educations__grades', 'academicinterventions').all()
    orphan_educations_status = []

    for orphan in orphans:
        latest_intervention = orphan.academicinterventions.order_by(
            '-last_modified').first()
        critical_needed = any(grade.grade < 70 for education in orphan.educations.all(
        ) for grade in education.grades.all())
        significant_needed = any(70 <= grade.grade < 75 for education in orphan.educations.all(
        ) for grade in education.grades.all())

        # Determine if there's a change in academic status that requires a new intervention
        new_intervention_needed = (latest_intervention is None or
                                   (latest_intervention.status == 'resolved' and
                                    (critical_needed or significant_needed)))

        if latest_intervention and not new_intervention_needed:
            intervention_status = latest_intervention.status
            remarks = latest_intervention.description
        else:
            # Set default status if no intervention exists
            intervention_status = 'unresolved' if critical_needed else 'pending' if significant_needed else 'none'
            remarks = "Academic performance requires intervention." if intervention_status != 'none' else "No academic intervention needed."

            # Create a new intervention record only if it's needed
            # Create a new intervention record only if it's needed
            if new_intervention_needed:
                latest_intervention = AcademicIntervention.objects.create(
                    orphan=orphan,
                    status=intervention_status,
                    description=remarks,
                    last_modified=now()
                )

        academic_status = 'Critical Improvement Needed' if critical_needed else (
            'Needs Improvement' if significant_needed else 'Meets Expectations')
        academic_status_color = academic_status_colors[academic_status]
        intervention_color = intervention_status_colors[intervention_status]

        orphan_educations_status.append({
            'orphan': orphan,
            'academic_status': academic_status,
            'academic_status_color': academic_status_color,
            'intervention_status': intervention_status,
            'intervention_color': intervention_color,
            'last_modified': latest_intervention.last_modified if latest_intervention else now(),
            'remarks': remarks,
        })

    # Sort orphans by priority
    orphan_educations_status.sort(key=lambda item: (
        {'Critical Improvement Needed': 1, 'Needs Improvement': 2,
            'Meets Expectations': 3}.get(item['academic_status'], 99),
        {'unresolved': 1, 'pending': 2, 'resolved': 3,
            'none': 4}.get(item['intervention_status'], 99)
    ))

    return render(request, 'Dashboard/intervention_academics.html', {'orphan_educations_status': orphan_educations_status})


def intervention_history(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    interventions = orphan.academicinterventions.order_by(
        '-last_modified').all()

    return render(request, 'Dashboard/intervention_academics_history.html', {
        'orphan': orphan,
        'interventions': interventions,
    })


def get_behavior_intervention_count(request):
    current_year = datetime.now().year
    count = BehaviorIntervention.objects.filter(
        status='unresolved',
    ).values('orphan').distinct().count()  # Ensure distinct count by orphan
    return count


def get_academic_intervention_count(request):
    count = AcademicIntervention.objects.filter(
        status='unresolved').values('orphan').distinct().count()
    return count


def get_health_intervention_count(request):
    count = HealthIntervention.objects.filter(
        status='unresolved').values('orphan').distinct().count()
    return count


def chart_bmi(request):
    # This fetches all BMI records and their related orphan info
    bmi_records = BMI.objects.all().select_related('orphan')
    print("bmi records:", bmi_records)

    return render(request, 'Dashboard/chart_bmi.html', {'bmi_records': bmi_records})


def chart_health(request):
    return render(request, 'Dashboard/chart_health.html')


def chart_age(request):
    orphans = Info.objects.all().order_by('age')  # Order by the 'age' field
    context = {'orphans': orphans}
    return render(request, 'Dashboard/chart_age.html', context)


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
