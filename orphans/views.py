import logging
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models.functions import Trunc
from django.db.models import Count, Case, When, CharField
from deep_translator import GoogleTranslator
from textblob import TextBlob
from .models import Education, Grade, get_sentiment_data, HealthDetail
from django import forms, views
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse, FileResponse
from .forms import NoteForm, OrphanFileForm, OrphanProfileForm, FamilyForm, BmiForm, FilesForm, OrphanForm, EducationForm, GradeForm, ProfilePictureForm
from .models import Info, BMI, Education, Family, Subject, Grade
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import os
from django.views.decorators.http import require_http_methods
from django.core import serializers
from django.core.exceptions import PermissionDenied
import json
# Create your views here.
from django.utils.dateparse import parse_date
from .models import Files  # Make sure to import your Files model
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, date
from django.shortcuts import HttpResponseRedirect
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.views import View
from django.db.models import Q
from django.urls import reverse
from django.views import View
from django.db import transaction
from . import models
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Prefetch
from decimal import Decimal

sid = SentimentIntensityAnalyzer()
# Add new words to the Vader lexicon
new_words = {
    'shrewish': -1.0,
    # add any other words you want to add to the lexicon
}
sid.lexicon.update(new_words)


def add_note(request, orphan_id):
    orphan = Info.objects.get(orphanID=orphan_id)  # Fetch the Orphan instance
    error_message = None  # Initialize an error message variable

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)  # Don't save the form yet
            bisaya_text = note.text  # Get the Bisaya text

            try:
                # Translate the Bisaya text to English
                translated_text = GoogleTranslator(
                    source='ceb', target='english').translate(bisaya_text)

                # Conduct sentiment analysis using

                sentiment = sid.polarity_scores(translated_text)

                # Save the Bisaya text, translated text, and sentiment to the Note instance
                note.text = bisaya_text
                note.translated_note = translated_text
                # Use the compound score
                note.sentiment_score = sentiment['compound']
                # Set the related_orphan foreign key to the Info instance
                note.related_orphan = orphan

                note.save()
            except Exception as e:
                # Handle any errors that occurred during the translation or sentiment analysis process
                print(f"An error occurred: {e}")
        else:
            error_message = "The form is invalid. Please check the data you entered."

    else:
        form = NoteForm()
    return render(request, 'orphans/behavior_profile.html', {'form': form, 'orphan': orphan})


def standardize_grade(self):
    # Define the max and min scores for high school
    high_school_max_score = 100
    high_school_min_passing_score = 75

    # Define the max and min scores for college
    college_max_score = 1.00
    college_min_score = 3.00

    if self.education_level == 'college':
        # Check for failing grade
        if self.grade >= college_min_score:
            # Assign a standardized score below the high school passing threshold
            return high_school_min_passing_score - 1
        # Convert the grade using the linear transformation formula
        standardized_grade = ((high_school_max_score - high_school_min_passing_score) /
                              (college_min_score - college_max_score)) * (self.grade - college_max_score) + high_school_max_score
    else:  # 'elementary' or 'high_school'
        # Check for failing grade
        if self.grade < high_school_min_passing_score:
            return self.grade - 1  # Slightly lower to differentiate from the lowest passing grade
        standardized_grade = ((self.grade - 75) / (98 - 75)) * (high_school_max_score -
                                                                high_school_min_passing_score) + high_school_min_passing_score

    return standardized_grade


def filter_orphans(request):
    status_filter = request.GET.get('status', '')
    if status_filter:
        orphans = Info.objects.filter(status=status_filter)
    else:
        orphans = Info.objects.all()

    # Serialize the queryset to JSON
    data = serializers.serialize('json', orphans)
    return JsonResponse(data, safe=False)


class Orphan_Search(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            results = Info.objects.filter(
                Q(firstName__icontains=query) |
                Q(middleName__icontains=query) |
                Q(lastName__icontains=query)
            )

            data = []
            for orphan in results:
                try:
                    # Adjusted to match the URL pattern keyword argument
                    orphan_url = reverse('orphan_profile', kwargs={
                                         'orphanID': orphan.orphanID})
                    data.append({
                        'label': f"{orphan.firstName} {orphan.middleName or ''} {orphan.lastName}",
                        'value': orphan_url  # This will be used for redirection
                    })
                except Exception as e:
                    print(f"Error generating URL for orphan {
                          orphan.orphanID}: {e}")

            return JsonResponse(data, safe=False)
        else:
            return JsonResponse([], safe=False)


class File_Search(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            results = Files.objects.filter(
                Q(fileName__icontains=query) |
                Q(fileDescription__icontains=query)
            )

            data = []
            for file in results:
                try:
                    # Generate a URL for downloading or opening the file
                    file_url = reverse('file_details', args=[str(file.fileID)])
                    data.append({
                        'label': f"{file.fileName} {file.fileDescription or ''}",
                        'value': file.fileID  # This will be used for redirection
                    })
                except Exception as e:
                    print(f"Error generating URL for file {file.fileID}: {e}")

            return JsonResponse(data, safe=False)
        else:
            return JsonResponse([], safe=False)


def save_academic_details(request, orphan_id):
    if request.method == 'POST':
        # Extract standard fields
        school_name = request.POST.get('school_name')
        education_level = request.POST.get('education_level')
        year_level = request.POST.get('year_level')
        quarter_or_semester = request.POST.get('quarter')

        # Initialize lists to hold all subjects and grades
        all_subjects = []
        all_grades = []

        # Add the initial subject and grade to the lists
        initial_subject = request.POST.get('subject')
        initial_grade = request.POST.get('grade')
        if initial_subject and initial_grade:
            all_subjects.append(initial_subject)
            all_grades.append(initial_grade)

        # Extend the lists with additional subjects and grades
        additional_subjects = request.POST.getlist('subject[]')
        additional_grades = request.POST.getlist('grade[]')
        all_subjects.extend(additional_subjects)
        all_grades.extend(additional_grades)

        if not all([school_name, education_level, year_level, all_subjects, all_grades]):
            return HttpResponseBadRequest("Missing required fields")

        orphan = get_object_or_404(Info, pk=orphan_id)

        with transaction.atomic():
            education = Education.objects.create(
                orphan=orphan,
                school_name=school_name,
                education_level=education_level,
                year_level=year_level,
            )
            is_college = education_level == 'College'

            for subject_name, grade_value in zip(all_subjects, all_grades):
                subject, _ = Subject.objects.get_or_create(
                    name=subject_name.strip())
                # Conditionally save quarter or semester
                # Conditional Logic for Quarter vs. Semester
                if is_college:
                    field_to_save = 'semester'
                else:
                    field_to_save = 'quarter'

                Grade.objects.create(
                    subject=subject,
                    education=education,
                    grade=Decimal(grade_value),
                    **{field_to_save: request.POST.get('quarter')},
                )

        return redirect('academic_profile', orphan_id=orphan_id)

    return render(request, 'orphans/academic_profile.html')


def academic_profile(request, orphan_id):
    # Fetch the orphan instance by ID or return a 404 error if not found
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Fetch all education records related to this orphan
    # Use `prefetch_related` to optimize queries for related grades
    educations = Education.objects.filter(
        orphan=orphan).prefetch_related('grades')

    # Prepare the context for rendering in the template
    context = {
        'orphan': orphan,
        'educations': educations,
    }

    # Render the academic_profile template with the context
    return render(request, 'orphans/academic_profile.html', context)


def family_detail(request, family_id):
    family = Family.objects.get(id=family_id)
    return render(request, 'family_detail.html', {'family': family})


def orphan_view(request):
    entries_per_page = int(request.GET.get('entries', 10))
    page_number = int(request.GET.get('page', 1))

    # Prefetch OrphanFiles to reduce database queries in the loop
    birth_certificates = models.OrphanFiles.objects.filter(
        type_of_document='Birth Certificate')
    orphans_query = Info.objects.filter(is_deleted=False).order_by('orphanID').prefetch_related(
        Prefetch('orphan_files', queryset=birth_certificates,
                 to_attr='birth_certificate_files')
    )
    print(orphans_query)
    paginator = Paginator(orphans_query, entries_per_page)

    try:
        orphans = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        orphans = paginator.page(paginator.num_pages)

    # Use the prefetched birth certificate information to annotate each orphan
    for orphan in orphans.object_list:
        # Here, 'birth_certificate_files' is the list of prefetched birth certificates from 'OrphanFiles'
        orphan.has_birth_certificate_attr = bool(
            orphan.birth_certificate_files)

    return render(request, 'orphans/orphan.html', {  # Ensure the template name is correct
        'orphans': orphans,
        'entries_per_page': entries_per_page
    })


def change_profile_picture(request, orphan_id):
    # Use orphan_id to fetch the orphan
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=orphan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile picture updated successfully.')
        return redirect('orphan_profile', orphanID=orphan.orphanID)
    else:
        form = ProfilePictureForm(instance=orphan)

    context = {
        'form': form,
        'orphan': orphan
    }
    return render(request, 'orphans/orphan-content.html', context)


def orphan_profile(request, orphanID):
    # Fetch the orphan instance using the provided orphanID.
    orphan = Info.objects.prefetch_related(
        'physical_health', 'orphan_files').get(orphanID=orphanID)

    # Determine the status based on the absence of any missing documents
    new_status = orphan.get_dynamic_status()
    if orphan.status != 'G' and orphan.status != new_status:
        orphan.status = new_status
        orphan.save()
    # # Determine the status based on the presence of a birth certificate
    # if orphan.status != 'G' and orphan.has_birth_certificate():
    #     orphan.status = 'A'
    #     orphan.save()

    # Save the updated status
    orphan.save()

    # Fetch the latest education instance for the orphan.
    latest_education = orphan.educations.order_by('-id').first()

    # Fetch the physical health records for the orphan.
    physical_health_records = orphan.physical_health.all()

    # Fetch the latest BMI record for the orphan.
    latest_physical_health = orphan.physical_health.order_by(
        '-recorded_at').first()

    # Assuming MEDIA_URL is set up correctly in your settings.py
    # Attempt to fetch the birth certificate file's URL if it exists
    birth_certificate_file = orphan.orphan_files.filter(
        type_of_document='Birth Certificate').first()
    birth_certificate_url = birth_certificate_file.file.url if birth_certificate_file else None

    # Fetch all files related to the current orphan
    files = models.OrphanFiles.objects.filter(orphan=orphan)
    # Prepare the context with the orphan and latest education instance.

    if request.method == 'POST':
        if 'graduate_orphan' in request.POST:
            print(f"Received request to graduate orphan with ID: {orphanID}")
            orphan.status = 'G'
            orphan.save()
            print(f"Status after update: {orphan.status}")
            return JsonResponse({'status': 'ok'}, safe=False)
        else:
            # Handle file upload form
            form = OrphanFileForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                redirect_url = reverse('orphan_profile', kwargs={
                                       'orphanID': orphanID})
                return JsonResponse({"message": "File successfully uploaded", "redirect_url": redirect_url}, status=200)
            else:
                print(form.errors)
                return JsonResponse({"error": "Failed to upload file", "details": form.errors.as_json()}, status=400)

        # Log status after update
        print(f"Status after update: {orphan.status}")
        # Respond with JSON indicating success
        return JsonResponse({'status': 'ok'}, safe=False)

    context = {
        'orphan': orphan,
        'latest_education': latest_education,
        'physical_health_records': physical_health_records,
        'latest_physical_health': latest_physical_health,  # Add this line
        'birth_certificate_url': birth_certificate_url,
        'orphanID': orphanID,
        'files': files,
        # Include any other context data you need for the template.

    }

    # Render the template with the context.
    return render(request, 'orphans/orphan-content.html', context)


def add_health_details(request):
    print(request.POST)  # Print all POST data
    print(request.POST.getlist('symptoms'))
    orphan_id = request.POST.get('orphan_id')
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Fetch all symptom values from the form
    submitted_symptoms = request.POST.getlist('symptoms')

    # For each symptom, check if it's in the submitted symptoms and set accordingly
    health_detail = HealthDetail(
        orphan=orphan,
        sick_start_date=request.POST.get('sickStartDateInput'),
        temperature=request.POST.get('temperatureInput'),
        blood_pressure=request.POST.get('bloodPressureInput'),
        # Update how symptoms are assigned
        # nausea='nausea' in request.POST.getlist('symptoms'),  # Update
        vomiting='vomiting' in request.POST.getlist('symptoms'),  # Update
        headache='headache' in request.POST.getlist('symptoms'),  # Update
        stomachache='stomachache' in request.POST.getlist(
            'symptoms'),  # Update
        cough='cough' in request.POST.getlist('symptoms'),  # Update
        dizziness='dizziness' in request.POST.getlist('symptoms'),  # Update
        body_pain='body_pain' in request.POST.getlist('symptoms'),  # Update
        other_details=request.POST.get('otherDetailsInput', '')
    )
    health_detail.save()

    return redirect('health_profile', orphan_id=orphan_id)


def mark_health_resolved(request):
    print("mark_health_resolved view called")  # Debugging line
    orphan_id = None  # Initialize orphan_id outside the 'if' block

    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        print("record_id:", record_id, type(record_id))  # Debugging line

        try:
            record = HealthDetail.objects.get(pk=record_id)
            orphan_id = record.orphan.orphanID  # Get the orphan_id
            record.sick_resolved = True  # Mark as resolved
            record.resolved = date.today()  # Update the resolved_date
            record.save()  # Save the changes
            print("Record after saving:", record)

            print("Found HealthDetail:", record)
            return JsonResponse({'success': True})
        except HealthDetail.DoesNotExist:
            return JsonResponse({'success': False})

    # Ensure orphan_id is assigned a value before using it in the redirect function
    if orphan_id is None:
        # Assign a default value or handle the case where orphan_id is None
        # For example, you might redirect to a default page or return an error response
        return JsonResponse({'success': False})

    print('orphan id is', orphan_id)
    return redirect('health_profile', orphan_id=orphan_id)


def health_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    # Fetch the health details related to the orphan
    health_details = orphan.health_details.all()
    return render(request, 'orphans/health_profile.html', {
        'orphan': orphan,
        'health_details': health_details,  # Pass the health details to the template
    })


def behavior_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    return render(request, 'orphans/behavior_profile.html', {'orphan': orphan})


def bmi_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    physical_health_records = orphan.physical_health.all()
    latest_physical_health = orphan.physical_health.order_by(
        '-recorded_at').first()

    bmi_values = [record.calculate_bmi(
    ) for record in physical_health_records if record.calculate_bmi() is not None]
    return render(request, 'orphans/bmi.html', {'orphan': orphan, 'physical_health_records': physical_health_records})


def add_bmi(request, orphan_id):
    orphan = Info.objects.get(orphanID=orphan_id)
    if request.method == 'POST':
        height = Decimal(request.POST.get('height'))
        weight = Decimal(request.POST.get('weight'))
        physical_health = BMI(
            orphan=orphan, height=height, weight=weight)
        physical_health.calculate_bmi()
        physical_health.save()
        return redirect('bmi_profile', orphan_id=orphan.orphanID)
    else:
        form = BmiForm()
    return render(request, 'add_bmi.html', {'form': form})


def edit_orphan(request, orphan_id):
    orphan = get_object_or_404(Info, orphanID=orphan_id)
    if request.method == 'POST':
        # Get data from form and update the orphan object
        # ...
        orphan.save()
        return redirect('orphans')
    else:
        # Render the form with the current orphan data
        return render(request, 'orphans/edit_orphan.html', {'orphan': orphan})


def delete_orphan(request, orphan_id):
    orphan = get_object_or_404(Info, orphanID=orphan_id)
    orphan.is_deleted = True
    orphan.save()
    return redirect('orphans')

# files


def files_view(request):
    files = Files.objects.filter(is_archived=False)
    return render(request, 'orphans/files.html', {'files': files})


def delete_files(request):
    if request.method == 'POST':
        file_id = request.POST.get('file_ids')  # Changed to get a single value
        if file_id:
            try:
                file_id = int(file_id)  # Ensure it's an integer
                print(f"Deleting file with ID: {file_id}")  # Debug print

                file = get_object_or_404(Files, fileID=file_id)
                file.is_archived = True
                file.deleted_at = timezone.now()
                file.save()
                messages.success(request, "File deleted successfully")
            except ValueError:
                messages.error(request, "Invalid file ID.")
        else:
            messages.error(request, "No file ID provided.")
    else:
        messages.error(request, "Invalid request.")

    return redirect('files_view')


def restore_files(request):
    if request.method == 'POST':
        # Attempt to get a list of file IDs
        file_ids = request.POST.getlist('file_ids')
        if not file_ids:
            # Fallback to a single file ID if no list is found
            single_file_id = request.POST.get('file_ids')
            if single_file_id:
                # Make it a list to keep the processing consistent
                file_ids = [single_file_id]

        print('Received file IDs:', file_ids)  # Debug print

        # Convert file_ids to integers, filtering out any invalid entries
        valid_file_ids = []
        for file_id in file_ids:
            try:
                valid_file_ids.append(int(file_id))
            except ValueError:
                # Handle or log the invalid file ID as needed
                pass

        if valid_file_ids:
            result = Files.objects.filter(
                fileID__in=valid_file_ids).update(is_archived=False)
            print('Number of files restored:', result)  # Debug print
            messages.success(request, "Files restored successfully")
        else:
            messages.error(request, "No valid file IDs provided.")

        return redirect('trash_view')
    else:
        messages.error(request, "Invalid request.")
        return redirect('trash_view')


def upload_file(request):
    if request.method != 'POST':
        return HttpResponse(status=405)  # Method not allowed

    try:
        file = request.FILES.get('file')
        file_name = request.POST.get('fileName', '')

        if not file:
            return HttpResponse(status=400)  # Bad request

        file_instance = Files(fileName=file_name, file=file)
        file_instance.save()
        return HttpResponse(status=200)  # OK - Success
    except Exception as e:
        return HttpResponse(status=500)  # Internal server error


@require_POST
def rename_file(request):
    # Ensure it's a POST request
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request")

    new_name = request.POST.get('newFileName')
    file_id = request.POST.get('fileID')

    # Validate file_id is not empty and is a digit
    if not file_id or not file_id.isdigit():
        return HttpResponseBadRequest("Invalid file ID")

    file_id = int(file_id)  # Convert file_id to an integer

    try:
        file_to_rename = Files.objects.get(fileID=file_id)
    except Files.DoesNotExist:
        return HttpResponseBadRequest("File not found")

    # Proceed to rename the file
    file_to_rename.fileName = new_name
    file_to_rename.save()

    # Redirect or respond as necessary
    return redirect('files_view')


def file_details(request, file_id):
    print(f"Fetching details for file ID: {file_id}")  # Debugging line

    try:
        file = Files.objects.get(fileID=file_id)
    except Files.DoesNotExist:
        raise Http404("File not found")

    try:
        data = {
            'fileName': file.fileName,
            'fileType': file.file.url.split('.')[-1],
            'fileSize': file.file.size,
            'dateUploaded': file.uploaded_at.strftime('%Y-%m-%d'),
        }
    except ValueError:
        return JsonResponse({'error': 'No file associated with this object'}, status=400)

    return JsonResponse(data)


def serve_file(request, file_id):
    file = get_object_or_404(Files, pk=file_id)
    # Make sure the user is authorized to access this file
    if request.user.is_authenticated and request.user.has_perm('can_view_file'):
        file_path = os.path.join(settings.MEDIA_ROOT, file.file.path)
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'inline; filename="{}"'.format(
            file.fileName)
        return response
    else:
        raise PermissionDenied


def serve_orphan_files(request, file_id):
    # Optional: Check user permissions here

    # Retrieve the file object, ensure you're catching the correct identifier
    orphan_file = get_object_or_404(models.OrphanFiles, pk=file_id)

    # Optional: Perform any additional checks here (e.g., file existence)

    # Serve the file
    try:
        return FileResponse(orphan_file.file.open(), as_attachment=False, filename=orphan_file.file.name)
    except FileNotFoundError:
        raise Http404("File does not exist")


def trash_view(request):
    sort_order = request.GET.get('sort', 'desc')  # Default to descending

    if sort_order == 'asc':
        archived_files = Files.objects.filter(
            is_archived=True).order_by('deleted_at')
    else:  # 'desc' or any other case
        archived_files = Files.objects.filter(
            is_archived=True).order_by('-deleted_at')

    return render(request, 'orphans/Trash.html', {'files': archived_files})


def download_file(request, file_id):
    file = Files.objects.get(fileID=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file.fileName)
    else:
        messages.error(request, "File not found")
        return redirect('files')


# Configure logging
logger = logging.getLogger(__name__)


def permanent_file_deletion(request):
    file_ids = request.POST.getlist('file_ids')
    if file_ids:
        # Your deletion logic, assuming it loops through file_ids and deletes files
        for file_id in file_ids:
            file = get_object_or_404(Files, fileID=file_id, is_archived=True)
            file.delete()
        messages.success(request, "File(s) deleted successfully.")
    else:
        messages.error(request, "No files selected for deletion.")

    return redirect('trash_view')


def save_changes(request, orphan_id):
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Debug print orphan's name before update
    print('Orphan name before update:', orphan.firstName,
          orphan.middleName, orphan.lastName)

    # Get the new data from the POST request
    data = json.loads(request.body)
    print('Data received:', data)

    # Update the orphan's personal information
    orphan.firstName = data.get('firstName', orphan.firstName)
    orphan.middleName = data.get('middleName', orphan.middleName)
    orphan.lastName = data.get('lastName', orphan.lastName)
    orphan.gender = data.get('gender', orphan.gender)
    orphan.birthDate = parse_date(
        data['birthDate']) if 'birthDate' in data else orphan.birthDate
    orphan.dateAdmitted = parse_date(
        data['dateAdmitted']) if 'dateAdmitted' in data else orphan.dateAdmitted

    # Update the Family's information if provided
    if any(key in data for key in ['mothersName', 'fathersName', 'mothersAddress', 'fathersAddress', 'mothersDob', 'mothersContact', 'mothersOccupation', 'fathersDob', 'fathersContact', 'fathersOccupation']):
        if orphan.family is None:
            orphan.family = Family.objects.create()
            orphan.save()
        family = orphan.family
        family.mother_name = data.get('mothersName', family.mother_name)
        family.father_name = data.get('fathersName', family.father_name)
        family.mother_address = data.get(
            'mothersAddress', family.mother_address)
        family.father_address = data.get(
            'fathersAddress', family.father_address)
        family.mother_dob = data.get(
            'mothersDob', family.mother_dob) if data.get('mothersDob') else None
        family.mother_contact = data.get(
            'mothersContact', family.mother_contact)
        family.mother_occupation = data.get(
            'mothersOccupation', family.mother_occupation)
        family.father_dob = data.get(
            'fathersDob', family.father_dob) if data.get('fathersDob') else None
        family.father_contact = data.get(
            'fathersContact', family.father_contact)
        family.father_occupation = data.get(
            'fathersOccupation', family.father_occupation)
        family.save()

    orphan.save()
    # Update the BMI's information if provided
    if 'height' in data or 'weight' in data or 'bmi_category' in data:
        physical_health, created = BMI.objects.get_or_create(
            orphan=orphan)
        if 'height' in data and data['height']:
            try:
                physical_health.height = float(data['height'])
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid height format'})
        if 'weight' in data and data['weight']:
            try:
                physical_health.weight = float(data['weight'])
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Invalid weight format'})
        if 'bmi_category' in data:
            physical_health.bmi_category = data['bmi_category']
        physical_health.calculate_bmi()
        physical_health.save()
    # Return a JSON response
    return JsonResponse({'status': 'ok'})


def addOrphanForm(request):
    if request.method == 'POST':
        info_form = OrphanForm(request.POST, request.FILES)
        family_form = FamilyForm(request.POST)

        if info_form.is_valid() and family_form.is_valid():
            family = family_form.save()
            info = info_form.save(commit=False)
            info.family = family
            info.save()
            info_form.save_m2m()  # Save any many-to-many relationships

            # Handling the birth certificate
            birth_certificate_file = request.FILES.get('birth_certificate')
            if birth_certificate_file:
                models.OrphanFiles.objects.create(
                    orphan=info,
                    file=birth_certificate_file,
                    file_name=birth_certificate_file.name,
                    type_of_document='Birth Certificate',
                    description='Birth certificate for {}'.format(
                        info.firstName)
                )

            # Handling any other file
            other_file = request.FILES.get('file')
            if other_file:
                models.OrphanFiles.objects.create(
                    orphan=info,
                    file=other_file,
                    file_name=other_file.name,
                    # Or dynamically set based on user input if needed
                    type_of_document='Other Document',
                    description='Additional document for {}'.format(info.name)
                )

            messages.success(
                request, "Orphan profile has been successfully created.")
            return redirect('orphans')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        info_form = OrphanForm()
        family_form = FamilyForm()
        # No need to initialize OrphanFileForm here since files are handled manually in the view

    return render(request, 'orphans/orphan.html', {
        'info_form': info_form,
        'family_form': family_form,
    })
