from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from orphans.forms import FilesForm
from .models import Info, Files
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse
import os
from django.core.exceptions import PermissionDenied


# Create your views here.


@login_required
def orphan_view(request):
    orphans = Info.objects.all()
    return render(request, "orphans/orphan.html", {'orphans': orphans})


def orphan_profile(request, orphanID):
    orphan = get_object_or_404(Info.objects.select_related(
        'physical_health'), orphanID=orphanID)
    return render(request, 'orphans/orphan-content.html', {'orphan': orphan})


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
    # Pass the files to the template
    return render(request, 'orphans/Trash.html', {'files': archived_files})


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
