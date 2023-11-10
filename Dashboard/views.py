# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# @login_required
def Dashboard_view(request):
    # Add any logic you need for the home view
    return render(request, "Dashboard/Dashboard.html", {})
