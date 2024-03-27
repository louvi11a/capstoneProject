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
from .forms import NoteForm, OrphanProfileForm, FamilyForm, BmiForm, FilesForm, OrphanForm, EducationForm, GradeForm, UploadBirthCertificateForm
from .models import Info, BMI, Education, Family, Subject, Grade
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import os
from django.views.decorators.http import require_http_methods

from django.core.exceptions import PermissionDenied
import json
# Create your views here.
from django.utils.dateparse import parse_date
from .models import Files  # Make sure to import your Files model
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime
from django.shortcuts import HttpResponseRedirect
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.views import View
from django.db.models import Q
from django.urls import reverse
from django.views import View
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

                # # Conduct sentiment analysis using TextBlob
                # blob = TextBlob(translated_text)
                # sentiment = blob.sentiment.polarity

                # Conduct sentiment analysis using NLTK's Vader SentimentIntensityAnalyzer
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


def add_health_details(request):
    orphan_id = request.POST.get('orphan_id')
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Fetch all symptom values from the form
    # This will be a list of values for checked boxes
    submitted_symptoms = request.POST.getlist('symptoms')

    # For each symptom, check if it's in the submitted symptoms and set accordingly
    health_detail = HealthDetail(
        orphan=orphan,
        date=request.POST.get('dateInput'),
        temperature=request.POST.get('temperatureInput'),
        blood_pressure=request.POST.get('bloodPressureInput'),
        heart_rate=request.POST.get('heartRateInput'),
        nausea='nausea' in submitted_symptoms,
        vomiting='vomiting' in submitted_symptoms,
        headache='headache' in submitted_symptoms,
        stomachache='stomachache' in submitted_symptoms,
        cough='cough' in submitted_symptoms,
        dizziness='dizziness' in submitted_symptoms,
        pain='pain' in submitted_symptoms,
        # others_symptoms=request.POST.get('othersCheckbox', ''),
        other_details=request.POST.get('otherDetailsInput', '')
    )
    health_detail.save()

    return redirect('health_profile', orphan_id=orphan_id)


def upload_birth_certificate(request, orphan_id):
    orphan = Info.objects.get(pk=orphan_id)

    if request.method == 'POST':
        form = UploadBirthCertificateForm(request.POST, request.FILES)

        if form.is_valid():
            orphan.birth_certificate = form.cleaned_data['birth_certificate']
            orphan.status = 'C'  # Update status to 'Complete'
            orphan.save()

            return redirect('orphan_detail', orphan_id=orphan_id)

    else:
        form = UploadBirthCertificateForm()

    return render(request, 'upload.html', {'form': form})


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
    if request.method != 'POST':
        # If not POST, just render the form page or redirect
        return render(request, 'orphans/academic_profile.html')

    # Extract all form data
    school_name = request.POST.get('school_name')
    education_level = request.POST.get('education_level')
    year_level = request.POST.get('year_level')
    quarter = request.POST.get('quarter')
    subject_name = request.POST.get('subject')
    grade_value = request.POST.get('grade')

    # Basic server-side validation
    if not all([school_name, education_level, year_level, quarter, subject_name, grade_value]):
        return HttpResponseBadRequest("Missing required academic details.")

    try:
        grade_value = int(grade_value)
    except ValueError:
        return HttpResponseBadRequest("Invalid grade value.")

    orphan = get_object_or_404(Info, orphanID=orphan_id)

    with transaction.atomic():
        try:
            subject, created = Subject.objects.get_or_create(name=subject_name)

            education = Education(
                orphan=orphan,
                school_name=school_name,
                education_level=education_level,
                year_level=year_level,
            )
            education.save()

            # Instead of adding the subject to education directly, create a Grade instance
            grade = Grade(
                subject=subject,
                education=education,
                grade=grade_value,
                quarter=quarter,
            )
            grade.save()

        except Exception as e:
            # Log the error or send a message to the user
            return HttpResponse(str(e), status=500)

    # Redirect to a success page or the academic profile
    return redirect('academic_profile', orphan_id=orphan_id)


def academic_profile(request, orphan_id):
    # Fetch the orphan instance by ID or return a 404 error if not found
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Fetch all education records related to this orphan
    # Use `prefetch_related` to optimize queries for related grades
    educations = Education.objects.filter(
        orphan=orphan).prefetch_related('grade_set')

    # Prepare the context for rendering in the template
    context = {
        'orphan': orphan,
        'educations': educations,
    }

    # Render the academic_profile template with the context
    return render(request, 'orphans/academic_profile.html', context)


def orphan_view(request):
    # Get the number of entries from the query string, default to 10
    entries_per_page = int(request.GET.get('entries', 10))  # convert to int
    page_number = int(request.GET.get('page', 1))  # convert to int
    orphans = Info.objects.filter(is_deleted=False).order_by('orphanID')
    # Create a Paginator object
    paginator = Paginator(orphans, entries_per_page)  # create a Paginator

    try:
        # get the Page object for the current page
        page_obj = paginator.page(page_number)
    except (EmptyPage, InvalidPage):
        # if the page number is invalid, show the last page
        page_obj = paginator.page(paginator.num_pages)

    # pass the Page object to the template
    return render(request, 'orphans/orphan.html', {'page_obj': page_obj, 'entries_per_page': entries_per_page})


def family_detail(request, family_id):
    family = Family.objects.get(id=family_id)
    return render(request, 'family_detail.html', {'family': family})

# def orphan_view(request, orphan_id):
#     orphans = Info.objects.filter(is_deleted=False)
#     orphan = Info.objects.get(id=orphan_id)
#     family = orphan.family  # assuming there is a 'family' field in your Info model
#     return render(request, "orphans/orphan.html", {'orphan': orphan, 'family': family})


def orphan_profile(request, orphanID):
    # Fetch the orphan instance using the provided orphanID.
    orphan = Info.objects.prefetch_related(
        'physical_health').get(orphanID=orphanID)

    # Fetch the latest education instance for the orphan.
    latest_education = orphan.educations.order_by('-id').first()

    # Fetch the physical health records for the orphan.
    physical_health_records = orphan.physical_health.all()

    # Fetch the latest BMI record for the orphan.
    latest_physical_health = orphan.physical_health.order_by(
        '-recorded_at').first()

    # Prepare the context with the orphan and latest education instance.
    context = {
        'orphan': orphan,
        'latest_education': latest_education,
        'physical_health_records': physical_health_records,
        'latest_physical_health': latest_physical_health,  # Add this line

        # Include any other context data you need for the template.
    }

    # Render the template with the context.
    return render(request, 'orphans/orphan-content.html', context)


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


def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

    try:
        file = request.FILES.get('file')
        file_name = request.POST.get('fileName', '')

        if not file:
            return JsonResponse({'message': 'No file uploaded.'}, status=400)

        file_instance = Files(fileName=file_name, file=file)
        file_instance.save()
        return JsonResponse({'message': 'File uploaded successfully.'})
    except Exception as e:
        return JsonResponse({'message': 'Server error: ' + str(e)}, status=500)


@require_POST
def rename_file(request):
    # Parse the JSON body of the request
    data = json.loads(request.body)
    file_id = data.get('fileId')
    new_name = data.get('newFileName')

    try:
        file_obj = Files.objects.get(id=file_id)
        file_obj.fileName = new_name
        file_obj.save()
        return JsonResponse({'success': True, 'message': 'File renamed successfully.'})
    except Files.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'File not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'}, status=500)


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


def restore_files(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids')
        print('Received file IDs:', file_ids)  # Debug print
        result = Files.objects.filter(
            fileID__in=file_ids).update(is_archived=False)
        print('Number of files restored:', result)  # Debug print
        messages.success(request, "Files restored successfully")
    return redirect('trash_view')


def trash_view(request):
    # Get all Files where is_archived is True
    archived_files = Files.objects.filter(is_archived=True)
    # Get all orphan profiles where is_deleted is True
    # Print deleted_at for each archived file
    for file in archived_files:
        print(f"File ID: {file.fileID}, Deleted at: {file.deleted_at}")
    deleted_orphans = Info.objects.filter(is_deleted=True)
    # Pass the files and orphan profiles to the template
    return render(request, 'orphans/Trash.html', {'files': archived_files, 'orphans': deleted_orphans})


def download_file(request, file_id):
    file = Files.objects.get(fileID=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, str(file.file))
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file.fileName)
    else:
        messages.error(request, "File not found")
        return redirect('files')

# trash


# # this is for editing the orphan content.html


def save_changes(request, orphan_id):
    # Debug prints
    # print('Request method:', request.method)
    # print('Request body:', request.body)

    # Get the orphan
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
        info_form = OrphanProfileForm(request.POST, request.FILES)
        family_form = FamilyForm(request.POST)
        files_form = FilesForm(request.POST, request.FILES)  # handle FilesForm

        if info_form.is_valid() and family_form.is_valid() and files_form.is_valid():
            family = family_form.save()
            info = info_form.save(commit=False)
            info.family = family
            info.save()

            # If the Files model should be linked to the Info instance
            file_instance = files_form.save(commit=False)
            # Assuming 'related_orphan' is the FK field in Files model
            file_instance.related_orphan = info
            file_instance.save()

            return redirect('orphans')
        else:
            if not info_form.is_valid():
                print('Info form errors:', info_form.errors)
            if not family_form.is_valid():
                print('Family form errors:', family_form.errors)
            if not files_form.is_valid():
                print('Files form errors:', files_form.errors)
    else:
        info_form = OrphanProfileForm()
        family_form = FamilyForm()
        files_form = FilesForm()  # initialize FilesForm

    print('POST data:', request.POST)
    print('FILES data:', request.FILES)

    return render(request, 'orphans/orphan.html', {'info_form': info_form, 'family_form': family_form, 'files_form': files_form})
