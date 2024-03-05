from django.http import Http404
from .forms import OrphanProfileForm, FamilyForm
from .models import Info, PhysicalHealth, Education, Family
from decimal import Decimal, InvalidOperation
from .models import Info, Education, PhysicalHealth
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from orphans.forms import FilesForm
from .models import Info, Files, Education, PhysicalHealth
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse
import os
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
import json
# Create your views here.
from django.utils.dateparse import parse_date
import logging
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse
from .models import Files  # Make sure to import your Files model
from django.views.decorators.http import require_POST


@login_required
def orphan_view(request):
    orphans = Info.objects.filter(is_deleted=False)
    for orphan in orphans:
        if orphan.orphan_picture and hasattr(orphan.orphan_picture, 'url'):
            # Print the URL of the orphan's profile picture
            print(orphan.orphan_picture.url)
    return render(request, "orphans/orphan.html", {'orphans': orphans})


def orphan_profile(request, orphanID):
    # Fetch the orphan instance using the provided orphanID.
    orphan = get_object_or_404(Info.objects.select_related(
        'physical_health'), orphanID=orphanID)

    # Fetch the latest education instance for the orphan.
    latest_education = orphan.educations.order_by('-id').first()

    # Prepare the context with the orphan and latest education instance.
    context = {
        'orphan': orphan,
        'latest_education': latest_education,
        # Include any other context data you need for the template.
    }

    # Render the template with the context.
    return render(request, 'orphans/orphan-content.html', context)


def academic_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    return render(request, 'orphans/academic.html', {'orphan': orphan})


def health_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    return render(request, 'orphans/health.html', {'orphan': orphan})


def behavior_profile(request, orphan_id):
    orphan = get_object_or_404(Info, pk=orphan_id)
    return render(request, 'orphans/orphanSentiment.html', {'orphan': orphan})


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


def delete_files(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids')
        print('Received file IDs:', file_ids)  # Debug print

        files_to_delete = Files.objects.filter(fileID__in=file_ids)
        for file in files_to_delete:
            file.is_archived = True
            file.deleted_at = timezone.now()
            file.save()

        print('Number of files deleted:', files_to_delete.count())  # Debug print
        messages.success(request, "Files deleted successfully")
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
    print('Request method:', request.method)
    print('Request body:', request.body)

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
    orphan.mothersName = data.get('mothersName', orphan.mothersName)
    orphan.fathersName = data.get('fathersName', orphan.fathersName)
    orphan.homeAddress = data.get('homeAddress', orphan.homeAddress)
    orphan.save()
    print('Saved orphan:', orphan)

    # Update the PhysicalHealth's information if provided
    if 'height' in data or 'weight' in data or 'bmi_category' in data:
        physical_health, created = PhysicalHealth.objects.get_or_create(
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

    # Update the Education's information if provided
    education_fields = ['education_level', 'school_name',
                        'current_gpa', 'school_year', 'quarter']
    education_data = {field: data.get(
        field) for field in education_fields if field in data and data[field] != ''}
    if education_data:
        # Fetch the latest education instance or create a new one if none exist
        education = orphan.educations.order_by('-id').first()
        if not education:
            education = Education(orphan=orphan)

        for key, value in education_data.items():
            if key == 'current_gpa':
                try:
                    education.current_gpa = Decimal(value)
                except (ValueError, InvalidOperation):
                    return JsonResponse({'status': 'error', 'message': 'Invalid GPA format'})
            elif key == 'quarter':
                education.quarter = int(value)
            else:
                setattr(education, key, value)
        education.save()
        print('Saved education:', education)

    # Return a JSON response
    return JsonResponse({'status': 'ok'})
# if hasattr(orphan, 'physical_health'):
#         # Get the associated PhysicalHealth instance
#         physical_health = orphan.physical_health
#     else:
#         # If not, create a new PhysicalHealth instance and associate it with the orphan
#         physical_health = PhysicalHealth(orphan=orphan)

#     # Update the PhysicalHealth's information
#     if 'height' in data:
#         physical_health.height = float(data.get('height'))
#     if 'weight' in data:
#         physical_health.weight = float(data.get('weight'))
#     if 'bmi_category' in data:
#         physical_health.bmi_category = data.get('bmi_category')
#     physical_health.calculate_bmi()

#     # Save the changes to the PhysicalHealth instance
#     physical_health.save()


@login_required
# def addOrphanForm(request):
def addOrphanForm(request):
    if request.method == 'POST':
        info_form = OrphanProfileForm(request.POST, request.FILES)
        family_form = FamilyForm(request.POST)
        if info_form.is_valid() and family_form.is_valid():
            family = family_form.save()
            info = info_form.save(commit=False)
            info.family = family
            info.save()
            return redirect('orphan_list_view')
    else:
        info_form = OrphanProfileForm()
        family_form = FamilyForm()
    return render(request, 'orphans/orphan_form.html', {'info_form': info_form, 'family_form': family_form})

# def delete_files(request):
#     if request.method == 'POST':
#         file_ids = request.POST.getlist('file_ids')
#         print('Received file IDs:', file_ids)  # Debug print
#         result = Files.objects.filter(
#             fileID__in=file_ids).update(is_archived=True)
#         print('Number of files archived:', result)  # Debug print

#         if result > 0:
#             messages.success(request, f"{result} files archived successfully")
#         else:
#             messages.warning(request, "No files were archived")

#     return redirect('files')


# def add_orphan(request):
#     if request.method == 'POST':
#         # Get data from form
#         first_name = request.POST.get('firstName')
#         last_name = request.POST.get('lastName')
#         middle_name = request.POST.get('middleName')
#         gender = request.POST.get('gender')
#         birth_date = request.POST.get('birthDate')
#         mothers_name = request.POST.get('mothersName')
#         fathers_name = request.POST.get('fathersName')
#         date_admitted = request.POST.get('dateAdmitted')
#         home_address = request.POST.get('homeAddress')
#         orphan_picture = request.FILES.get(
#             'orphan_picture')  # Get the uploaded file

#         # Create new Info object and save it to the database
#         orphan = Info(
#             firstName=first_name,
#             lastName=last_name,
#             middleName=middle_name,
#             gender=gender,
#             birthDate=birth_date,
#             mothersName=mothers_name,
#             fathersName=fathers_name,
#             dateAdmitted=date_admitted,
#             homeAddress=home_address,
#             # Assign the uploaded file to the orphan_picture field
#             orphan_picture=orphan_picture,
#         )
#         orphan.save()

#         # Redirect to the page that shows the list of orphans
#         return redirect('orphans')

#     # If the request method is not POST, render the form
#     return render(request, 'orphans/orphan.html')
