from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from orphans.forms import FilesForm
from .models import Info
from .models import Files
# from .forms import FilesForm
from django.contrib import messages

# Create your views here.


@login_required
def orphan_view(request):
    orphans = Info.objects.all()
    return render(request, "orphans/orphan.html", {'orphans': orphans})


# @login_required

def orphan_profile(request, orphanID):
    orphan = get_object_or_404(Info.objects.select_related(
        'physical_health'), orphanID=orphanID)
    return render(request, 'orphans/orphan-content.html', {'orphan': orphan})

# def orphanProfile_view(request):
#     # Add any logic you need for the home view
#     return render(request, "orphans/orphan-content.html", {})


# @login_required
# def files_view(request):
#     # Add any logic you need for the home view
#     return render(request, "orphans/Files.html", {})


@login_required
def trash_view(request):
    # Add any logic you need for the home view
    return render(request, "orphans/Trash.html", {})


def files_view(request):
    if request.method == 'POST':
        form = FilesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File uploaded successfully")
            form = FilesForm()  # reset the form
    else:
        form = FilesForm()

    files = Files.objects.filter(is_archived=False)
    return render(request, 'orphans/Files.html', {'files': files, 'form': form})


def trash_view(request):
    # Get all Files where is_archived is True
    archived_files = Files.objects.filter(is_archived=True)

    # Pass the files to the template
    return render(request, 'orphans/Trash.html', {'files': archived_files})
