from .models import Info, PhysicalHealth  # Import your Info model
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from orphans.forms import FilesForm
from .models import Info, Files
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse
import os
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
# Create your views here.
from django.utils.dateparse import parse_date


@login_required
def orphan_view(request):
    orphans = Info.objects.filter(is_deleted=False)
    for orphan in orphans:
        if orphan.orphan_picture and hasattr(orphan.orphan_picture, 'url'):
            # Print the URL of the orphan's profile picture
            print(orphan.orphan_picture.url)
    return render(request, "orphans/orphan.html", {'orphans': orphans})


def orphan_profile(request, orphanID):
    orphan = get_object_or_404(Info.objects.select_related(
        'physical_health'), orphanID=orphanID)
    return render(request, 'orphans/orphan-content.html', {'orphan': orphan})


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


def files_view(request):
    if request.method == 'POST':
        form = FilesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File uploaded successfully")
            return redirect('files')  # Redirect after POST
    else:
        form = FilesForm()

    files = Files.objects.filter(is_archived=False)
    return render(request, 'orphans/Files.html', {'files': files, 'form': form})


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


def trash_view(request):
    # Get all Files where is_archived is True
    archived_files = Files.objects.filter(is_archived=True)
    # Get all orphan profiles where is_deleted is True
    deleted_orphans = Info.objects.filter(is_deleted=True)
    # Pass the files and orphan profiles to the template
    return render(request, 'orphans/Trash.html', {'files': archived_files, 'orphans': deleted_orphans})


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
        result = Files.objects.filter(
            fileID__in=file_ids).update(is_archived=True)
        print('Number of files archived:', result)  # Debug print

        if result > 0:
            messages.success(request, f"{result} files archived successfully")
        else:
            messages.warning(request, "No files were archived")

    return redirect('files')


def add_orphan(request):
    if request.method == 'POST':
        # Get data from form
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        middle_name = request.POST.get('middleName')
        gender = request.POST.get('gender')
        birth_date = request.POST.get('birthDate')
        mothers_name = request.POST.get('mothersName')
        fathers_name = request.POST.get('fathersName')
        date_admitted = request.POST.get('dateAdmitted')
        home_address = request.POST.get('homeAddress')
        orphan_picture = request.FILES.get(
            'orphan_picture')  # Get the uploaded file

        # Create new Info object and save it to the database
        orphan = Info(
            firstName=first_name,
            lastName=last_name,
            middleName=middle_name,
            gender=gender,
            birthDate=birth_date,
            mothersName=mothers_name,
            fathersName=fathers_name,
            dateAdmitted=date_admitted,
            homeAddress=home_address,
            # Assign the uploaded file to the orphan_picture field
            orphan_picture=orphan_picture,
        )
        orphan.save()

        # Redirect to the page that shows the list of orphans
        return redirect('orphans')

    # If the request method is not POST, render the form
    return render(request, 'orphans/orphan.html')

# this is for editing the orphan content.html


def save_changes(request, orphan_id):
    print('Request method:', request.method)  # Debug print
    print('Request body:', request.body)  # Debug print

    # Get the orphan
    orphan = get_object_or_404(Info, orphanID=orphan_id)

    # Print the orphan's name before updating
    print('Orphan name before update:', orphan.firstName,
          orphan.middleName, orphan.lastName)

    # Get the new data from the POST request
    data = json.loads(request.body)
    print('Data:', data)  # Debug print

    # Update the orphan's information
    if 'firstName' in data:
        orphan.firstName = data.get('firstName')
    if 'middleName' in data:
        orphan.middleName = data.get('middleName')
    if 'lastName' in data:
        orphan.lastName = data.get('lastName')
    if 'gender' in data:
        orphan.gender = data.get('gender')
    if 'birthDate' in data:
        birth_date = data.get('birthDate')
        if isinstance(birth_date, str) and birth_date:
            orphan.birthDate = parse_date(birth_date)
    if 'dateAdmitted' in data:
        date_admitted = data.get('dateAdmitted')
        if isinstance(date_admitted, str) and date_admitted:
            orphan.dateAdmitted = parse_date(date_admitted)
    if 'mothersName' in data:
        orphan.mothersName = data.get('mothersName')
    if 'fathersName' in data:
        orphan.fathersName = data.get('fathersName')
    if 'homeAddress' in data:
        orphan.homeAddress = data.get('homeAddress')

    # Print the orphan's name after updating
    print('Orphan name after update:', orphan.firstName,
          orphan.middleName, orphan.lastName)

    # Check if the orphan has an associated PhysicalHealth instance
    if hasattr(orphan, 'physical_health'):
        # Get the associated PhysicalHealth instance
        physical_health = orphan.physical_health
    else:
        # If not, create a new PhysicalHealth instance and associate it with the orphan
        physical_health = PhysicalHealth(orphan=orphan)

    # Update the PhysicalHealth's information
    if 'height' in data:
        physical_health.height = float(data.get('height'))
    if 'weight' in data:
        physical_health.weight = float(data.get('weight'))
    if 'bmi_category' in data:
        physical_health.bmi_category = data.get('bmi_category')
    physical_health.calculate_bmi()

    # Save the changes to the PhysicalHealth instance
    physical_health.save()
    # print('Saved physical_health:', physical_health)  # Debug print

    # Check if the orphan has an associated Education instance
    education = orphan.educations.first()
    if education is not None and 'school_year' in data:
        # Update the Education's information
        education.school_year = data.get('school_year')
        # Save the changes to the Education instance
        education.save()
        print('Saved education:', education)  # Debug print

    # Save the changes to the orphan
    orphan.save()
    print('Saved orphan:', orphan)  # Debug print

    # Return a JSON response
    return JsonResponse({'status': 'ok'})
