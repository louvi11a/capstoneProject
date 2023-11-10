from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Info
from .models import Files
from .forms import FilesForm

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


@login_required
def files_view(request):
    # Add any logic you need for the home view
    return render(request, "orphans/Files.html", {})


@login_required
def trash_view(request):
    # Add any logic you need for the home view
    return render(request, "obeds/trash.html", {})


def files_view(request):
    # Fetch all non-archived Files records from the database
    files = Files.objects.filter(is_archived=False)
    return render(request, 'orphans/Files.html', {'files': files})


def upload_file(request):
    if request.method == 'POST':
        form = FilesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # replace with your success url
    else:
        form = FilesForm()
    return render(request, 'orphans/upload.html', {'form': form})
