from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_page_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to the home page upon successful login
            return redirect('Dashboard')
        else:
            # Handle incorrect login credentials here (e.g., display an error message)
            pass  # You can add your desired code here, or simply use the 'pass' keyword to do nothing

    return render(request, "users/loginPage.html", {})


def settings_view(request):
    # Add any logic you need for the home view
    return render(request, "users/Setting.html", {})

# def home_view(request):
#     # Add any logic you need for the home view
#     return render(request, "obeds/home.html", {})


# def orphan_view(request):
#     # Add any logic you need for the home view
#     return render(request, "obeds/orphan.html", {})


# def notes_view(request):
#     # Add any logic you need for the home view
#     return render(request, "obeds/notes.html", {})


# def files_view(request):
#     # Add any logic you need for the home view
#     return render(request, "obeds/files.html", {})


# # def Dboard_view(request):
# #     # Add any logic you need for the home view
# #     return render(request, "Dashboard/Dashboard.html", {})


# def trash_view(request):
#     # Add any logic you need for the home view
#     return render(request, "obeds/trash.html", {})
